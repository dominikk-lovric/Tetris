from elements.column import Column
from elements.text import *
from elements.image import *
from elements.element import *

class Content(Element):
    def __init__(self, title, size=None, color=None):
        self.size=size or 24
        if isinstance(title, str) and (title.lower().endswith(".png") or title.lower().endswith(".jpg") or title.lower().endswith(".jpeg")):
            self.content=Image(title, size)
        elif isinstance(title, list):
            children=[]
            for line in title:
                children.append(Text(line, size=self.size))
            self.content=Column(children, 0)
        else:
            self.content=Text(title, self.size, color or (255,255,255))

    def set_size(self, size):
        self.size = size
        self.content.set_size(size)

    def set_color(self, color):
        self.color = color
        self.content.set_color(color)

    def get_size(self):
        return self.content.get_size()

    def draw(self, surface, pos):
        self.content.draw(surface, pos)