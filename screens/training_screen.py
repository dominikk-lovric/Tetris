import os

import numpy as np

from screens import menu_screen
from elements.text import Text

from environment import PlaceChoiceEnv
from DNQ_agent import Agent
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import threading

times = {
    "get_state": 0,
    "choose_action": 0,
    "env_step": 0,
    "training": 0
}

MODEL_DIR = "models/reinforcement/dnq/place"
CKPT = os.path.join(MODEL_DIR, "tetris_model.pth")
BEST = os.path.join(MODEL_DIR, "tetris_best.pth")

class TrainingScreen(menu_screen.MenuScreen):
    title = "TRAINING"

    def __init__(self, game):
        super().__init__(game)
        self.data_lock = threading.Lock()
        self.lines=[]
        self.reward=[]
        self.max_lines=[]
        self.round=[]
        print("PyTorch version:", torch.__version__)
        print("CUDA available:", torch.cuda.is_available())

        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))

        self.training_thread = None
        self.training = False

    def options(self):
        return [
            (Text("Start"), lambda: self.start_training()),
            (Text("Stop"), lambda: self.stop_training()),
            (Text("Back"), lambda: self.Game.pop_screen())
        ]

    def stop_training(self):
        self.training = False
        self.get_graphs()

    def get_graphs(self, num=None):
        dir = f'graphs/{num}' if num is not None else "graphs"
        os.makedirs(dir, exist_ok=True)

        with self.data_lock:
            rounds = list(self.round)
            series = {
                "Lines": list(self.lines),
                "Reward": list(self.reward),
                "Max Lines": list(self.max_lines),
            }

        n = min(len(rounds), *(len(v) for v in series.values()))
        rounds = rounds[:n]
        series = {k: v[:n] for k, v in series.items()}

        # individual graphs (unchanged)
        for name, values in series.items():
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(rounds, values, marker="o")
            ax.set_xlabel("Rounds")
            ax.set_ylabel(name)
            ax.set_title(f"{name} vs Round")
            ax.grid(True)
            fig.tight_layout()

            filename = f"{name}{num}.png" if num is not None else f"{name}.png"
            fig.savefig(os.path.join(dir, filename), dpi=150)
            plt.close(fig)


        if n > 0:
            window = max(1, min(20, n // 5))
            kernel = np.ones(window) / window

            fig, axes = plt.subplots(len(series), 1, figsize=(8, 9), sharex=True)
            for ax, (name, values) in zip(axes, series.items()):
                ax.plot(rounds, values, marker="o", markersize=3, alpha=0.35, label="raw")
                if window > 1 and n >= window:
                    smooth = np.convolve(values, kernel, mode="valid")
                    ax.plot(rounds[window - 1:], smooth, linewidth=2, label=f"rolling mean ({window})")
                ax.set_ylabel(name)
                ax.grid(True)
                ax.legend(loc="upper left")

            axes[0].set_title("Training overview")
            axes[-1].set_xlabel("Rounds")
            fig.tight_layout()

            filename = f"All{num}.png" if num is not None else "All.png"
            fig.savefig(os.path.join(dir, filename), dpi=150)
            plt.close(fig)





    def start_training(self):
        if self.training:
            return

        self.training = True

        self.training_thread = threading.Thread(
            target=self.trainPlaceChoice,
            daemon=True
        )

        self.training_thread.start()



    def trainPlaceChoice(self):
        try:
            os.makedirs(MODEL_DIR, exist_ok=True)
            env = PlaceChoiceEnv(self.Game)
            state = env.reset()

            batch_size = 256
            training_rate = 4
            save_rate = 100
            episodes = 200

            agent = Agent(
                input_size=len(state),
                n_actions=env.n_actions,
                gamma=0.99,
                batch_size=batch_size,
                buffer_size=500_000,
            )

            if os.path.exists(CKPT):
                self.load(agent, CKPT)
                print("Loaded model")

            make_env = lambda seed: PlaceChoiceEnv(self.Game, seed=seed)
            best = -1.0
            global_step = 0

            for round_id in range(150000):
                if not self.training:
                    break
                if round_id % 100 == 0:
                    self.get_graphs(round_id // 100)

                print("-------- ROUND:", round_id, "--------")
                res = self.evaluate(agent, make_env)
                print(f'lines: {res["lines"]:.2f} | reward: {res["score"]:.2f} | '
                      f'max lines: {res["max_lines"]} | steps: {res["steps"]:.1f} | '
                      f'train steps: {agent.steps}')

                with self.data_lock:
                    self.lines.append(res["lines"])
                    self.reward.append(res["score"])
                    self.max_lines.append(res["max_lines"])
                    self.round.append(round_id)

                if res["median_lines"] > best:
                    best = res["median_lines"]
                    self.save(agent, BEST)

                for episode in range(episodes):
                    state = env.reset()
                    mask = env.legal_actions()
                    done = False

                    while not done and self.training:
                        action = agent.choose_action(state, mask)
                        next_state, reward, done = env.act(action)
                        next_mask = (np.ones(env.n_actions, dtype=bool)
                                     if done else env.legal_actions())

                        agent.remember(state, action, reward, next_state, done, next_mask)
                        global_step += 1
                        if global_step % training_rate == 0:
                            agent.training_step()

                        state, mask = next_state, next_mask

                    if (episode + 1) % save_rate == 0:
                        self.save(agent, CKPT)
        finally:
            self.training = False

    def save(self, agent, path):
        torch.save({
            "model": agent.model.state_dict(),
            "target": agent.target_model.state_dict(),
            "optim": agent.optimizer.state_dict(),
            "steps": agent.steps,
            "env_steps": agent.environment_steps,
        }, path)

    def load(self, agent, path, reset_exploration=False):
        ck = torch.load(path, map_location=agent.device)
        agent.model.load_state_dict(ck["model"])
        agent.target_model.load_state_dict(ck["target"])
        agent.optimizer.load_state_dict(ck["optim"])
        agent.steps = ck["steps"]
        agent.environment_steps = 0 if reset_exploration else ck["env_steps"]

    def evaluate(self, agent, make_env, n_games=20, seeds=None, max_steps=20_000):
        if seeds is None:
            seeds = range(n_games)

        scores, lines, steps = [], [], []

        for seed in list(seeds)[:n_games]:
            env = make_env(seed)
            state = env.reset()
            total, done = 0.0, False

            while not done and env.steps < max_steps:
                mask = env.legal_actions()
                action = agent.choose_action(state, mask, greedy=True)
                state, reward, done = env.act(action)
                total += reward

            scores.append(total)
            lines.append(env.lines)
            steps.append(env.steps)

        return {
            "score": float(np.mean(scores)),
            "lines": float(np.mean(lines)),
            "max_lines": int(np.max(lines)),
            "steps": float(np.mean(steps)),
            "median_lines": float(np.median(lines)),
            "std_lines": float(np.std(lines)),
        }