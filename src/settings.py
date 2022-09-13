import pygame


class Context:
    def __init__(self):
        self.tile_size = 64
        self.line_width = 4
        self.clock = pygame.time.Clock()

    @property
    def screen_width(self):
        try:
            return pygame.display.get_window_size()[0]
        except pygame.error:
            return 800

    @property
    def screen_height(self):
        try:
            return pygame.display.get_window_size()[1]
        except pygame.error:
            return 800

    @property
    def screen_size(self):
        return self.screen_width, self.screen_height


context = Context()
