from elements.element import Element
from functions.render_functions import render_text, get_font


class Text(Element):
    def __init__(
        self,
        text,
        size=24,
        color=(255, 255, 255),
        font="consolas",
        bold=False,
        italic=False,
        align="left",
    ):
        self.text = text
        self.size = size
        self.color = color
        self.font = font
        self.bold = bold
        self.italic = italic
        self.align = align

    def set_size(self, size):
        self.size = size

    def set_color(self, color):
        self.color = color

    def get_size(self):
        f = get_font(self.font, self.size, self.bold, self.italic)
        lines = self.text.split("\n")
        width = max(f.size(line)[0] for line in lines)
        height = f.get_linesize() * len(lines)
        return width, height

    def draw(self, surface, pos):
        return render_text(
            surface,
            self.text,
            pos,
            size=self.size,
            color=self.color,
            font=self.font,
            bold=self.bold,
            italic=self.italic,
            anchor="topleft",
            align=self.align,
        )