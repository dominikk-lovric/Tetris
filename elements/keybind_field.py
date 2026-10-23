import pygame

from elements.column import Column
from elements.padding import Padding
from elements.row import Row
from elements.text import Text
from settings import Settings


class KeybindField:
    def __init__(self, name, settings, setting, color=None, size=None ):
        self.name = name
        self.settings = settings
        self.setting = setting
        self.color = color or self.settings.get_touple("COLORS/FG")
        self.size = size or 24
        self.text=self.settings.get(setting) or "none"

        self.selected=False

    def set_selected(self, value):
        self.selected=value

    def set_color(self, color):
        self.color = color

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.get_centered(Text("press a key..." if self.selected else self.text,size = self.settings.get("UNIT")), self.size*5, self.size, self.color, 2).get_size()

    def draw(self, surface, pos):
        Key=self.get_centered(Text("press a key..." if self.selected else self.text,color= self.color,size = self.settings.get("UNIT")), self.size*10, self.size*2, border_color=self.color, border_size= 4 if self.selected else 2)
        Row([Text(self.name, color=self.color,size = self.size), Key], align="center", spacing=self.settings.get("UNIT")).draw(surface, pos)

    def get_selected(self):
        return self.selected

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        name=pygame.key.name(event.key)
        if event.key != pygame.K_BACKSPACE and event.key != pygame.K_ESCAPE and event.key != pygame.K_RETURN and name:
            self.text=name
            self.settings.set(self.setting, name)
            self.selected=False
        elif event.key in (pygame.K_BACKSPACE, pygame.K_RETURN, pygame.K_ESCAPE):
            self.selected=False

    def get_box(self, x, y, border_color=None, border_size=0):
        return Padding(Column([Row([Text("  ",size = self.settings.get("UNIT")) for j in range(x)]) for i in range(y)]), border_color=border_color,
                       border=border_size)

    def get_centered(self, item, sizeX, sizeY, border_color=None, border_size=0):
        sizeX = sizeX
        sizeY = sizeY
        itemSize = item.get_size()
        paddingVertical = (sizeY - itemSize[1]) / 2
        paddingHorizontal = (sizeX - itemSize[0]) / 2
        return Padding(item, vertical=paddingVertical, horizontal=paddingHorizontal, border=border_size,
                       border_color=border_color)
