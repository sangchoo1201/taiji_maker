import pygame

import src.file as file
from src.checker import Checker
from src.drawer import Drawer
from src.settings import context


class Player:
    def __init__(self, screen, path):
        self.screen = screen
        self.drawer = Drawer(screen).set_grid(file.reader(path))
        self.drag = None

    def get_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return quit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue
                x, y = pygame.mouse.get_pos()
                x, y = self.drawer.convert_coordinates(x, y)
                if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
                    continue
                sprite = self.drawer.grid[y][x]
                if sprite.fixed:
                    continue
                self.drag = sprite.lit
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return quit
            if event.key == pygame.K_SPACE:
                print(self.check())

    def run(self):
        result = self.get_event()
        if result is not None:
            return result

        if not pygame.mouse.get_pressed(3)[0]:
            self.drag = None

        pos = pygame.mouse.get_pos()
        x, y = self.drawer.convert_coordinates(*pos)
        if 0 <= x < self.drawer.width and 0 <= y < self.drawer.height:
            sprite = self.drawer.grid[y][x]
            if sprite.lit == self.drag:
                sprite.flip()

        self.screen.fill((63, 63, 63))
        self.drawer.draw()
        pygame.display.update()
        context.clock.tick(60)

    def check(self):
        checker = Checker(self.drawer.grid)
        return checker.check()
