import pyfiglet

from elements.text import Text
from game import Game
from screens.menu_screen import MenuScreen
from screens.settings_screen import SettingsScreen


class PauseScreen(MenuScreen):
    title="PAUSED"

    if not (title.endswith(".png") or title.endswith(".jpg")):
        list = []
        for letter in title:
            a = pyfiglet.figlet_format(letter)
            list.append([])
            a = a.split("\n")
            for b in a:
                list[-1].append(b)
        title = list

    def options(self):
        return [
            (Text("Resume", size=self.Game.settings.get("UNIT")), lambda: self.Game.pop_screen()),
            (Text("Settings", size=self.Game.settings.get("UNIT")), lambda: self.Game.push_screen(SettingsScreen(self.Game))),
            (Text("Give up", size=self.Game.settings.get("UNIT")), lambda: (self.Game.pop_screen(), self.Game.pop_screen())),
        ]