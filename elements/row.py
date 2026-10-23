from elements.element import Element


class Row(Element):
    def __init__(
        self,
        children=None,
        spacing=0,
        align="start",
        mainAxisAalignment="center",
    ):
        self.children = children or []
        self.spacing = spacing
        self.align = align
        self.mainAxisAalignment = mainAxisAalignment

    def get_size(self):
        height = 0
        width = 0
        for child in self.children:
            width += child.get_size()[0]
            height = max(height,child.get_size()[1])

        return width+self.spacing*(len(self.children)-1), height

    def set_color(self, color):
        for child in self.children:
            child.set_color(color)

    def set_size(self, size):
        for child in self.children:
            child.set_size(size)

    def draw(self, surface, pos):
        x,y=pos
        wX,wY = self.get_size()
        for child in self.children:
            chY=y
            if self.align == "center":
                chY = y + (wY - child.get_size()[1])/2
            elif self.align == "end":
                chY = y + wY - child.get_size()[1]
            else:
                chY = y
            child.draw(surface, (x,chY))
            x += child.get_size()[0]+self.spacing