from elements.element import Element


class Column(Element):
    def __init__(
        self,
        children=None,
        spacing=0,
        mainAxisAalignment="center",
        crossAxisAalignment="start",
    ):
        self.children = children or []
        self.spacing = spacing
        self.crossAxisAalignment = crossAxisAalignment
        self.mainAxisAalignment = mainAxisAalignment

    def get_size(self):
        height = 0
        width = 0
        for child in self.children:
            height += child.get_size()[1]
            width = max(width,child.get_size()[0])
        return width, height+self.spacing*(len(self.children)-1)

    def set_color(self, color):
        for child in self.children:
            child.set_color(color)

    def set_size(self, size):
        for child in self.children:
            child.set_size(size)

    def draw(self, surface, pos):
        x,y=pos
        if self.mainAxisAalignment == "spaceAround":
            allChildHeight=0
            for child in self.children:
                allChildHeight += child.get_size()[1]
            space=surface.get_rect().height-allChildHeight
            self.spacing=space/(len(self.children)+1)
            y+=self.spacing
        elif self.mainAxisAalignment == "spaceBetween":
            allChildHeight=0
            for child in self.children:
                allChildHeight += child.get_size()[1]
            space=surface.get_rect().height-allChildHeight
            self.spacing=space/(len(self.children)-1)
        elif self.mainAxisAalignment == "end":
            allChildHeight=0
            for child in self.children:
                allChildHeight += child.get_size()[1]
            posY=surface.get_rect().height-allChildHeight
            y+=posY

        wX,wY = self.get_size()
        for child in self.children:
            chX=x
            if self.crossAxisAalignment == "center":
                chX = x + (wX - child.get_size()[0])/2
            elif self.crossAxisAalignment == "end":
                chX = x + wX - child.get_size()[0]
            else:
                chX = x
            child.draw(surface, (chX,y))
            y += child.get_size()[1]+self.spacing