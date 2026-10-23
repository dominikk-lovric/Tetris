import pygame
from elements.element import Element


class TetrisField(Element):
    def __init__(self, game, width, height, cell="[]", wall="|", floor="__",
                 size=24, font_name="couriernew"):
        self.Game = game
        self.w, self.h = width, height
        self.cell_str, self.wall_str, self.floor_str = cell, wall, floor
        self.font_name = font_name
        self.grid = [[0] * width for _ in range(height)]
        self.set_size(size)

    def set_size(self, size):
        self.size = size
        s = self.Game.settings
        font = pygame.font.SysFont(self.font_name, size)

        self.cell_w = font.size(self.cell_str)[0]
        self.cell_h = font.get_linesize()
        self.bar_w = font.size(self.wall_str)[0]

        def make(text, color, w):
            surf = pygame.Surface((w, self.cell_h), pygame.SRCALPHA)
            img = font.render(text, True, color)
            surf.blit(img, ((w - img.get_width()) // 2, (self.cell_h - img.get_height()) // 2))
            return surf

        fg = s.get_touple("COLORS/FG")
        self.bar = make(self.wall_str, fg, self.bar_w)
        self.floor = make(self.floor_str, fg, self.cell_w)

        pieces = s.get("PIECES")
        self.glyphs = {
            i: make(self.cell_str, s.get_touple("COLORS/PIECE_COLORS/" + name), self.cell_w)
            for i, name in enumerate(pieces, start=1)
        }
        self.glyphs[len(pieces) + 1] = make(
            self.cell_str, s.get_touple("COLORS/PIECE_COLORS/PREVIEW"), self.cell_w
        )

    def set_grid(self, grid):
        self.grid = grid

    def get_size(self):
        return (self.w * self.cell_w + 2 * self.bar_w, self.h * self.cell_h)

    def draw(self, surface, pos):
        x0, y0 = pos
        right_x = x0 + self.bar_w + self.w * self.cell_w
        for r, row in enumerate(self.grid):
            y = y0 + r * self.cell_h
            surface.blit(self.bar, (x0, y))
            surface.blit(self.bar, (right_x, y))
            for c, value in enumerate(row):
                x = x0 + self.bar_w + c * self.cell_w
                if value:
                    surface.blit(self.glyphs[value], (x, y))
                elif r == self.h - 1:
                    surface.blit(self.floor, (x, y))