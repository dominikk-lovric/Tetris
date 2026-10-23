import os
import pygame

_image_cache = {}
_font_cache = {}


def load_img(path, size=None):
    key = (path, size)
    if key not in _image_cache:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        _image_cache[key] = img
    return _image_cache[key]


def get_font(name=None, size=24, bold=False, italic=False):
    key = (name, size, bold, italic)
    if key not in _font_cache:
        if name is None:
            font = pygame.font.Font(None, size)
            font.set_bold(bold)
            font.set_italic(italic)
        elif os.path.isfile(name):
            font = pygame.font.Font(name, size)
        else:
            font = pygame.font.SysFont(name, size, bold, italic)
        _font_cache[key] = font
    return _font_cache[key]


def render_img(surface, image, pos, size=None, scale=1.0, angle=0,
               alpha=255, flip=(False, False), anchor="topleft"):
    if isinstance(image, str):
        image = load_img(image)

    if size:
        image = pygame.transform.smoothscale(image, size)
    elif scale != 1.0:
        w, h = image.get_size()
        image = pygame.transform.smoothscale(image, (int(w * scale), int(h * scale)))

    if flip[0] or flip[1]:
        image = pygame.transform.flip(image, *flip)
    if angle:
        image = pygame.transform.rotate(image, angle)
    if alpha < 255:
        image = image.copy()
        image.set_alpha(alpha)

    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def render_text(surface, text, pos, size=24, color=(255, 255, 255), font=None,
                bold=False, italic=False, anchor="topleft",
                align="left", max_width=None, line_spacing=0):
    f = get_font(font, size, bold, italic)

    lines = []
    for paragraph in str(text).split("\n"):
        if not max_width:
            lines.append(paragraph)
            continue
        current = ""
        for word in paragraph.split(" "):
            test = f"{current} {word}"
            if f.size(test)[0] <= max_width or not current:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)

    rendered = []
    for line in lines:
        rendered.append(f.render(line, True, color))

    line_h = f.get_linesize() + line_spacing
    width = max(s.get_width() for s in rendered)
    height = line_h * (len(rendered) - 1) + rendered[-1].get_height()

    block = pygame.Surface((width, height), pygame.SRCALPHA)

    for i, surf in enumerate(rendered):
        if align == "center":
            x = (width - surf.get_width()) // 2
        elif align == "right":
            x = width - surf.get_width()
        else:
            x = 0
        y = i * line_h
        block.blit(surf, (x, y))

    rect = block.get_rect(**{anchor: pos})
    surface.blit(block, rect)
    return rect

