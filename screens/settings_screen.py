import pygame

import settings
from elements import keybind_field, selector
from elements.column import Column
from elements.row import Row
from elements.text import Text
from game import Game
from screen import Screen
from settings import Settings


class SettingsScreen(Screen):
    def __init__(self, game, selected=0):
        super().__init__(game)
        self.items = [
            keybind_field.KeybindField("Left", self.Game.settings, "KEYBINDS/REPEAT_KEYS/LEFT/binds/0"),
            keybind_field.KeybindField("Right", self.Game.settings, "KEYBINDS/REPEAT_KEYS/RIGHT/binds/0"),
            keybind_field.KeybindField("Rotate left", self.Game.settings, "KEYBINDS/KEYMAP/ROTATE_L/0"),
            keybind_field.KeybindField("Rotate right", self.Game.settings, "KEYBINDS/KEYMAP/ROTATE_R/0"),
            keybind_field.KeybindField("Rotate 180 degrees", self.Game.settings, "KEYBINDS/KEYMAP/ROTATE_180/0"),
            keybind_field.KeybindField("Hold", self.Game.settings, "KEYBINDS/KEYMAP/HOLD/0"),
            keybind_field.KeybindField("Soft drop", self.Game.settings, "KEYBINDS/REPEAT_KEYS/SOFT_DROP/binds/0"),
            keybind_field.KeybindField("Hard drop", self.Game.settings, "KEYBINDS/KEYMAP/HARD_DROP/0"),
        ]
        self.selected = selected
        for i in range(len(self.items)):
            self.items[i].set_color(
                self.Game.settings.get_touple("COLORS/FG") if i != self.selected else self.Game.settings.get_touple(
                    "COLORS/HIGHLIGHT"))
            self.items[i].set_size(
                self.Game.settings.get("UNIT") if i != self.selected else self.Game.settings.get("UNIT") * 2)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.items[self.selected].get_selected():
            self.items[self.selected].handle_event(event)
        else:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
                for i in range(len(self.items)):
                    self.items[i].set_color(self.Game.settings.get_touple("COLORS/FG") if i!=self.selected else self.Game.settings.get_touple("COLORS/HIGHLIGHT"))
                    self.items[i].set_size(self.Game.settings.get("UNIT") if i!=self.selected else self.Game.settings.get("UNIT")*2)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
                for i in range(len(self.items)):
                    self.items[i].set_color(self.Game.settings.get_touple("COLORS/FG") if i!=self.selected else self.Game.settings.get_touple("COLORS/HIGHLIGHT"))
                    self.items[i].set_size(self.Game.settings.get("UNIT") if i != self.selected else self.Game.settings.get("UNIT") * 2)
            elif event.key in (pygame.K_KP_ENTER, pygame.KSCAN_KP_ENTER, pygame.K_RETURN, pygame.K_SPACE):
                for i in range(len(self.items)):
                    self.items[i].set_color(self.Game.settings.get_touple("COLORS/FG") if i!=self.selected else self.Game.settings.get_touple("COLORS/HIGHLIGHT"))
                    if hasattr(self.items[i], 'set_selected'):
                        self.items[i].set_selected(i==self.selected)
            elif event.key == pygame.K_ESCAPE:
                self.Game.pop_screen()



    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(self.Game.settings.get_touple("COLORS/BG"))
        title=Text("Settings", size=self.Game.settings.get("UNIT") * 2)
        title.draw(surface, ((surface.get_rect().width-title.get_size()[0])/2, self.Game.settings.get("UNIT")*2))
        Col=Column([*self.items], mainAxisAalignment="center", crossAxisAalignment="end", spacing=self.Game.settings.get("UNIT")*3)
        Col.draw(surface, ((surface.get_rect().width/2-Col.get_size()[0]), self.Game.settings.get("UNIT")*10))