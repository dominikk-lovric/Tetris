from game import Game
from screens.main_menu import MainMenu


def main():
    game=Game()
    game.run_game(MainMenu(game))

if __name__ == "__main__":
    main()
