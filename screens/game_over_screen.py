import pyfiglet
import pygame
from elements.text import Text
from screens.menu_screen import MenuScreen
import screens.tetris_game_screen
from settings import Settings


class GameOverScreen(MenuScreen):

    new_score=0

    def __init__(self, app, size, score=0, selected=0):
        super().__init__(app)
        self.title="Game   Over"
        self.selected = selected
        self.font = pygame.font.SysFont("consolas,dejavusansmono,couriernew,monospace", 24)
        self.bg = self.Game.settings.get_touple("COLORS/BG")
        self.fg = self.Game.settings.get_touple("COLORS/FG")
        self.highlight = self.Game.settings.get_touple("COLORS/HIGHLIGHT")
        self.dim = self.Game.settings.get_touple("COLORS/DIM")
        self.shift=0
        self.size = size
        new_score=score
        self.score=new_score
        sizes=self.Game.settings.get("SIZES")
        for key in self.Game.settings.get("SIZES"):
            dict= self.Game.settings.get_touple("SIZES/"+key)
            if self.size==dict:
                self.size=key
                break
        if self.Game.settings.get("HIGHSCORE/"+self.size)<new_score:
            self.title="HIGHSCORE"
            self.Game.settings.set("HIGHSCORE/"+self.size, new_score)
        if not (self.title.endswith(".png") or self.title.endswith(".jpg")):
            list = []
            for letter in self.title:
                a = pyfiglet.figlet_format(letter)
                list.append([])
                a = a.split("\n")
                for b in a:
                    list[-1].append(b)
            self.title = list





    def aditional(self):
        if self.Game.settings.get("HIGHSCORE/"+self.size)<self.score:
            return[Text("Highscore:"+str(self.score), size=int(self.Game.settings.get("UNIT")*1.5))]
        else:
            return[Text("Score:"+str(self.score), size=(self.Game.settings.get("UNIT")*1.5)), Text("Highscore:"+str(self.Game.settings.get("HIGHSCORE/"+self.size)), size=self.Game.settings.get("UNIT"))]



    def options(self):
        return [
            (Text("Retry", size=self.Game.settings.get("UNIT")), lambda: self.Game.switch_screen(screens.tetris_game_screen.TetrisGameScreen(self.Game,size=self.Game.settings.get_touple("SIZES/"+self.size))),),
            (Text("Exit", size=self.Game.settings.get("UNIT")), lambda: self.Game.pop_screen()),
        ]