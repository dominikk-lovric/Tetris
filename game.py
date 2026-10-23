import pygame
import settings


class Game:


    def __init__(self):
        self.settings = settings.Settings()

        pygame.init()
        pygame.display.set_caption("ASCII Tetris")
        self.window = pygame.display.set_mode(self.settings.get_touple("MENU_SIZE"), pygame.RESIZABLE)
        self.stack = []
        self.running = True

    def push_screen(self,screen):
        self.stack.append(screen)
        screen.on_enter()

    def pop_screen(self):
        if self.stack:
            self.stack.pop()
        if self.stack:
            self.stack[-1].on_enter()

    def switch_screen(self,screen):
        self.pop_screen()
        self.push_screen(screen)

    def set_window_size(self, size):
        if self.window.get_size() != tuple(size):
            self.window = pygame.display.set_mode(size)

    def quit(self):
        self.running = False

    def run_game(self, first_screen):
        self.push_screen(first_screen)
        clock = pygame.time.Clock()
        while self.running and self.stack:
            self.settings.set("UNIT", min(int(self.window.get_size()[0]/50),int(self.window.get_size()[1]/50)))
            dt=clock.tick(60)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif self.stack:
                    self.stack[-1].handle_event(event)
            if not (self.running and self.stack):
                break
            top=self.stack[-1]
            top.update(dt)
            top.draw(self.window)
            pygame.display.flip()
        pygame.quit()