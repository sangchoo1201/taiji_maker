import pygame

import src.const as const
import src.file as file
from src.checker import Checker
from src.drawer import Drawer
from src.settings import context


class Player:
    def __init__(self, screen, path):
        self.screen = screen
        self.path = path
        self.drawer = Drawer(screen).set_grid(file.reader(path))
        self.drag = None

        self.result = ""

        context.is_editing = False

    def get_event(self):
        from main import end, select
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button not in (1, 3):
                    continue
                x, y = pygame.mouse.get_pos()
                x, y = self.drawer.convert_coordinates(x, y)
                if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
                    continue
                sprite = self.drawer.grid[y][x]
                if sprite.fixed and event.button == 1:
                    continue
                self.drag = sprite.lit if event.button == 1 else True
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return select
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.check()
            if event.key == pygame.K_r:
                self.drawer = Drawer(self.screen).set_grid(file.reader(self.path))

    def run(self):
        self.screen.fill(const.DARK)

        result = self.get_event()
        if result is not None:
            return result

        if not any(pygame.mouse.get_pressed(3)[:3:2]):
            self.drag = None

        pos = pygame.mouse.get_pos()
        x, y = self.drawer.convert_coordinates(*pos)
        if 0 <= x < self.drawer.width and 0 <= y < self.drawer.height:
            sprite = self.drawer.grid[y][x]
            if sprite.lit == self.drag:
                sprite.flip()

        self.drawer.draw()

        font = pygame.font.Font("resource/font/D2Coding.ttf", 64)
        text_image = font.render(self.result, True, (255, 255, 255))
        text_rect = text_image.get_rect(center=(context.screen_width // 2, context.screen_height - 36))
        self.screen.blit(text_image, text_rect)

        pygame.display.update()
        context.clock.tick(60)

    def check(self):
        checker = Checker(self.drawer.grid)
        self.result = str(checker.check())
