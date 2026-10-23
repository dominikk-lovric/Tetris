class Element:
    def draw(self, surface, pos):
        raise NotImplementedError

    def get_size(self):
        raise NotImplementedError