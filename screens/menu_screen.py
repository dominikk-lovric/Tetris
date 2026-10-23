import screen
from elements.column import Column
from elements.image import Image
from elements.padding import Padding
from elements.row import Row
from elements.text import Text
from functions.render_functions import *
import math
import colorsys

from game import Game
from settings import Settings


def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


class MenuScreen(screen.Screen):

    title = ""

    def __init__(self, app,  selected=0):
        super().__init__(app)
        self.selected = selected
        self.font = pygame.font.SysFont("consolas,dejavusansmono,couriernew,monospace", 24)
        self.bg = app.settings.get_touple("COLORS/BG")
        self.fg = app.settings.get_touple("COLORS/FG")
        self.highlight = app.settings.get_touple("COLORS/HIGHLIGHT")
        self.dim = app.settings.get_touple("COLORS/DIM")
        self.shift=0


    def options(self):
        return []

    def aditional(self):
        return []

    def update(self, dt):
        self.shift+=dt
        if self.shift > 1:
            self.shift = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        opts = self.options()
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(opts)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(opts)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            opts[self.selected][1]()
        elif event.key == pygame.K_ESCAPE:
            self.Game.pop_screen()
        elif pygame.K_1 <= event.key <= pygame.K_9:
            index = event.key - pygame.K_1
            if index < len(opts):
                self.selected = index
                opts[index][1]()
        if hasattr(opts[self.selected][0], "handle_event"):

            opts[self.selected][0].handle_event(event)

    def _blit_centered(self, surface, text, color, y):
        surf = self.font.render(text, True, color)
        surface.blit(surf, ((surface.get_width() - surf.get_width()) // 2, y))

    def draw(self, surface):
        surface.fill(self.bg)
        line_h = self.font.get_linesize()
        y = 40

        children=[]

        if(self.title!=None and self.title!=""):
            if isinstance(self.title, str) and (self.title.lower().endswith(".png") or self.title.lower().endswith(
                    ".jpg") or self.title.lower().endswith(".jpeg")):
                angle = math.sin(2 * math.pi * self.shift)
                children.append(Image(self.title, angle=angle))
            elif isinstance(self.title, list):
                item = []
                for i in range(len(self.title)):
                    line = self.title[i]
                    if (isinstance(line, list)):
                        lineline = []
                        letterShift = (math.sin(
                            (2 * math.pi * self.shift) + (2 * math.pi * (i / len(self.title)))) + 1) / 2
                        for itm in line:
                            colorHue = (((self.shift) + ((1 / 8) * ((i) / len(self.title)))))
                            color = hsv2rgb(math.fabs(colorHue), 1, 1)
                            lineline.append(Text(itm, color=color, size=self.Game.settings.get("UNIT")*2))

                        item.append(Padding(Column(lineline),
                                            top=int(letterShift * line_h*2),
                                            bottom=int((1 - letterShift) * line_h*2),
                                            ))
                    else:
                        item.append(Column([Text(line, size=self.Game.settings.get("UNIT"))]))

                row = Row(item)
                children.append(row)
            else:
                children.append(Text(self.title, size=self.Game.settings.get("UNIT")*5))

        children=children+self.aditional()

        for i, (label, _) in enumerate(self.options()):
            color = self.highlight if i == self.selected else self.fg
            if self.selected == i:
                label.set_color(color)
                label.set_size(int(self.Game.settings.get("UNIT")*2))
                children.append(Row([Text("~> ",color=color, size=self.Game.settings.get("UNIT")), label, Text(" <~", color=color, size=self.Game.settings.get("UNIT"))], align="center"))
            else:
                label.set_color(color)
                label.set_size(int(self.Game.settings.get("UNIT")*1.5))
                children.append(Padding(label, top=5, bottom=5))
        column=Column(children,30, mainAxisAalignment="spaceAround",crossAxisAalignment="center")
        column.draw(surface, (surface.get_rect().center[0]-column.get_size()[0]/2, 0))

