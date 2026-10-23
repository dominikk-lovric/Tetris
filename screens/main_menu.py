from elements.text import Text
from screens import menu_screen
import pyfiglet

from screens.game_settings_menu import GameSettingsMenu
from screens.settings_screen import SettingsScreen


class MainMenu(menu_screen.MenuScreen):
    title = "TETRIS"

    if not (title.endswith(".png") or title.endswith(".jpg")):
        list=[]
        for letter in title:
            a=pyfiglet.figlet_format(letter)
            list.append([])
            a=a.split("\n")
            for b in a:
                list[-1].append(b)
        title=list


    def options(self):
        return [
            (Text("Play"), lambda: self.Game.push_screen(GameSettingsMenu(self.Game))),
            (Text("Settings"), lambda: self.Game.push_screen(SettingsScreen(self.Game))),
            (Text("Exit"), lambda: self.Game.pop_screen()),
        ]
