from elements.image import Image
from elements.row import Row
from elements.selector import Selector
from elements.text import Text
from screens import menu_screen


from screens.tetris_game_screen import TetrisGameScreen


class GameSettingsMenu(menu_screen.MenuScreen):
    title = "Play options"

    def options(self):
        if not hasattr(self, "size_selector"):
            self.size_selector = Selector(
                [*self.Game.settings.get("SIZES").keys()],
                value=[(self.Game.settings.get("SIZES/"+item)["x"], self.Game.settings.get("SIZES/"+item)["y"]) for item in self.Game.settings.get("SIZES")],
                title="Size",
                selected=1
            )

        if not hasattr(self, "player_selector"):
            self.player_selector = Selector(
                ["Human"],
                value=["You"],
                title="Size",
                selected=0
            )

        return [
            (self.size_selector, lambda: ()),
            (self.player_selector, lambda: ()),
            (Text("Play", size=self.Game.settings.get("UNIT")), lambda: self.Game.push_screen(TetrisGameScreen(self.Game, width=self.size_selector.get_selected()[0], height=self.size_selector.get_selected()[1]))),
            (
                Row(
                    [Text("Back", size=self.Game.settings.get("UNIT")), Image("assets/back.png", size=24)],
                    align="center",
                    spacing=24
                ),
                self.Game.pop_screen
            ),
        ]
