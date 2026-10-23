from elements.element import Element
from functions.render_functions import render_img


class Image(Element):
    def __init__(self, path, size=None, scale=1.0, angle=0):
        self.path = path
        self.size = size
        self.scale = scale
        self.angle=angle

    def get_size(self):
        if self.size:
            return (self.size,self.size)

        from functions.render_functions import load_img

        image = load_img(self.path)
        return (
            int(image.get_width() * self.scale),
            int(image.get_height() * self.scale),
        )

    def set_size(self, size):
        self.size = size

    def set_color(self, color):
        pass

    def draw(self, surface, pos):
        return render_img(
            surface,
            self.path,
            pos,
            size=self.get_size(),
            scale=self.scale,
            anchor="topleft",
            angle=self.angle,
        )
