import pygame
from elements.column import Column
from elements.element import Element
from elements.row import Row
from elements.text import Text


class Selector(Element):
    def __init__(self, options, value=None, title="",color=None, size=None, selected=0):
        self.title = title
        self.options = options
        self.color = color
        self.size = size or 24
        self.selected = selected
        self.value = value



    def get_size(self):
        if(self.title!=""):
            if self.value is not None:
                text= self.options[self.selected]
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text=text+": ("
                text=text+str(self.value[self.selected])
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text=text+")"
            else:
                text= self.options[self.selected]
            item=Column([Text(self.title+":", size=self.size),Row([Text("<", size=self.size),Text(text, size=self.size),Text(">", size=self.size)])])
        else:
            if self.value is not None:
                text= self.options[self.selected]
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text = text + ": ("
                text = text + str(self.value[self.selected])
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text = text + ")"
            else:
                text= self.options[self.selected]
            item=Row([Text("<", size=self.size),Text(text, size=self.size),Text(">", size=self.size)])

        return item.get_size()

    def get_selected(self):
        if self.value is not None:
            return self.value[self.selected]
        else:
            return self.options[self.selected]

    def set_color(self, color):
        pass

    def set_size(self, size):
        pass

    def handle_event(self, event):
        if event.key in (pygame.K_d, pygame.K_RIGHT):
            self.selected = (self.selected+1)%len(self.options)

        elif event.key in (pygame.K_a, pygame.K_LEFT):
            self.selected= (self.selected-1)%len(self.options)


    def draw(self, screen, pos):
        if(self.title!=""):
            if self.value is not None:
                text= self.options[self.selected]
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text=text+": ("
                text=text+str(self.value[self.selected])
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text=text+")"
            else:
                text= self.options[self.selected]
            item=Column([Text(self.title+":", size=self.size),Row([Text("<", size=self.size),Text(text, size=self.size),Text(">", size=self.size)])])
        else:
            if self.value is not None:
                text= self.options[self.selected]
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text = text + ": ("
                text = text + str(self.value[self.selected])
                if isinstance(self.value[self.selected], str) or isinstance(self.value[self.selected], int):
                    text = text + ")"
            else:
                text= self.options[self.selected]
            item=Row([Text("<", size=self.size),Text(text, size=self.size),Text(">", size=self.size)])
        item.draw(screen, pos)
