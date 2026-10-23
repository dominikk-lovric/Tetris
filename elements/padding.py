import pygame

from elements.element import Element


class Padding(Element):

    def __init__(self, content, top=None, bottom=None, left=None, right=None,
                 vertical=None, horizontal=None, all=None, bg=None,
                 border=0, border_color=None, border_radius=0):
        self.top = top or vertical or all or 0
        self.bottom = bottom or vertical or all or 0
        self.left = left or horizontal or all or 0
        self.right = right or horizontal or all or 0
        self.content = content
        self.bg = bg or (0,0,0,0)
        self.border = border
        self.border_color = border_color or (255, 255, 255)
        self.border_radius = border_radius

    def get_size(self):
        cw, ch = self.content.get_size()
        b = self.border
        return (cw + self.left + self.right + 2 * b,
                ch + self.top + self.bottom + 2 * b)

    def draw(self, surface, pos):
        w, h = self.get_size()
        cw, ch = self.content.get_size()
        b = self.border
        rect = pygame.Rect(pos[0], pos[1], w, h)
        pygame.draw.rect(surface, self.bg, rect, border_radius=self.border_radius)
        if b > 0:
            pygame.draw.rect(surface, self.border_color, rect,
                             width=b, border_radius=self.border_radius)

        extra_w = w - (cw + self.left + self.right + 2 * b)
        extra_h = h - (ch + self.top + self.bottom + 2 * b)
        x = pos[0] + b + self.left + extra_w / 2
        y = pos[1] + b + self.top + extra_h / 2
        self.content.draw(surface, (x, y))