import os

from colorama import Fore

from screens import menu_screen
from elements.text import Text

from environment import PlaceChoiceEnv
from DNQ_agent import Agent

import torch
import threading


class TrainingScreen(menu_screen.MenuScreen):
    title = "TRAINING"

    def __init__(self, game):
        super().__init__(game)

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

            agent = Agent(
                input_size=len(state),
                n_actions=env.n_actions,
                learning_rate=0.0001,
                gamma=0.99,
                batch_size=1000,
                buffer_size=50000
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

            for round in range(150000):
                if not self.training:
                    break
                agent.environment_steps = 0
                print("--------------------------------ROUND:",round,"----------------------------------------------------")
                avg_lines=0
                avg_reward=0
                for episode in range(episodes):

                    state = env.reset()
                    done = False
                    total_reward = 0

                    while not done and self.training:
                        action_index = agent.choose_action(state)
                        next_state, reward, done = env.act(action_index)

                        agent.remember(state, action_index, reward, next_state, done)
                        agent.training_step()

                        state = next_state
                        total_reward += reward

                    print(Fore.WHITE +
                        f"Episode: {str(episode + 1)} | "
                        f"Reward: {(Fore.RED if total_reward<0 else Fore.GREEN) +str(total_reward)}"+ Fore.WHITE +" | "
                        + Fore.WHITE + f"Lines: {(Fore.RED if env.tetris.lines<=0 else Fore.GREEN) +str(env.tetris.lines)}"+ Fore.WHITE +" | "
                        + Fore.WHITE + f"Epsilon: {str(agent.get_epsilon())} |"
                        + Fore.WHITE +f"Steps: {str(env.steps)}|"
                    )

                    avg_lines+=env.tetris.lines
                    avg_reward+=total_reward

                    if (episode + 1) % 100 == 0:
                        torch.save({
                            "model": agent.model.state_dict(),
                            "target": agent.target_model.state_dict(),
                            "optimizer": agent.optimizer.state_dict(),
                            "steps": agent.steps,
                            "environment_steps": agent.environment_steps,
                        }, "tetris_model.pth")
                print("AVG LINES: ", avg_lines/episodes)
                print("AVG REWARD: ", avg_reward / episodes)
        finally:
            self.training = False