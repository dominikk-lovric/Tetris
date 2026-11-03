import os

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
        dir=f'graphs/{num}' if num is not None else "graphs"
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

        for name, values in series.items():
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(rounds, values[:n], marker="o")
            ax.set_xlabel("Rounds")
            ax.set_ylabel(name)
            ax.set_title(f"{name} vs Round")
            ax.grid(True)
            fig.tight_layout()

            filename = f"{name}{num}.png" if num is not None else f"{name}.png"
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
            env = PlaceChoiceEnv(self.Game)

            state = env.reset()

            batch_size=1000
            training_rate=4
            save_rate=100

            agent = Agent(
                input_size=len(state),
                n_actions=env.n_actions,
                learning_rate=0.0001,
                gamma=0.99,
                batch_size=batch_size,
                buffer_size=50000,
                epsilon_start=0.1,
            )

            if os.path.exists("tetris_model.pth"):
                ckpt = torch.load("tetris_model.pth", map_location=agent.device, weights_only=True)
                agent.model.load_state_dict(ckpt["model"])
                agent.target_model.load_state_dict(ckpt["target"])
                agent.optimizer.load_state_dict(ckpt["optimizer"])
                agent.steps = ckpt["steps"]
                agent.environment_steps = ckpt.get("environment_steps", 200_000)

                print("Loaded model")

            episodes = 1000
            global_step = 0
            for round_id in range(150000):
                if not self.training:
                    break
                if round_id % 100 == 0:
                    self.get_graphs(round_id//100)
                print("--------------------------------ROUND:",round_id,"----------------------------------------------------")
                avg_lines,avg_reward,max_lines, steps=self.evaluate(env, agent)
                print(f'lines: {round(avg_lines, 2)}| reward: {round(avg_reward,2)}| max lines: {max_lines}| steps: {steps}')
                with self.data_lock:
                    self.lines.append(avg_lines)
                    self.reward.append(avg_reward)
                    self.max_lines.append(max_lines)
                    self.round.append(round_id)
                for episode in range(episodes):



                    state = env.reset()
                    done = False
                    total_reward = 0

                    while not done and self.training:
                        action_index = agent.choose_action(state)
                        next_state, reward, done = env.act(action_index)

                        agent.remember(state, action_index, reward, next_state, done)
                        global_step += 1
                        if global_step % training_rate == 0:
                            agent.training_step()

                        state = next_state
                        total_reward += reward


                    if (episode + 1) % save_rate == 0:
                        torch.save({
                            "model": agent.model.state_dict(),
                            "target": agent.target_model.state_dict(),
                            "optimizer": agent.optimizer.state_dict(),
                            "steps": agent.steps,
                            "environment_steps": agent.environment_steps,
                        }, "tetris_model.pth")
        finally:
            self.training = False

    def evaluate(self, env, agent, n=20, max_steps=2000):
        lines = steps = max_lines = rewards = 0
        for _ in range(n):
            s = env.reset()
            done = False
            while not done and env.steps < max_steps:
                s, rew, done = env.act(agent.choose_action(s, greedy=True))
            lines += env.tetris.lines
            max_lines = max(max_lines, env.tetris.lines)
            steps += env.steps
            rewards+=rew
        return lines / n, rewards / n, max_lines, steps/n