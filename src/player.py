import pygame
import clipboard

import src.const as const
import src.file as file
from src.checker import Checker
from src.drawer import Drawer
from src.settings import context


class Player:
    def __init__(self, screen, path):
        context.is_editing = False

        self.screen = screen
        self.path = path
        self.drawer = Drawer(screen).set_grid(
            file.get(clipboard.paste()) if path is None else file.reader(path)
        )
        for row in self.drawer.grid:
            for sprite in row:
                sprite.draw()
        self.drag = (None, "")

        self.result = ""

    def get_event(self):  # sourcery skip: low-code-quality
        from main import end, select, main
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not 1 <= event.button <= 3:
                    continue
                x, y = self.drawer.convert_coordinates(*event.pos)
                if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
                    continue
                sprite = self.drawer.grid[y][x]
                if sprite.fixed and event.button == 1:
                    continue
                self.drag = ((sprite.lit, "lit"), (sprite.marked, "mark"), (sprite.exist, "exist"))[event.button - 1]
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return main if self.path is None else select
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.check()
            if event.key == pygame.K_r:
                self.drawer = Drawer(self.screen).set_grid(
                    file.get(clipboard.paste()) if self.path is None else file.reader(self.path)
                )
            if event.key == pygame.K_m:
                x, y = self.drawer.convert_coordinates(*pygame.mouse.get_pos())
                if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
                    continue
                sprite = self.drawer.grid[y][x]
                self.drag = sprite.marked, "mark"

    def run(self):
        self.screen.fill(const.DARK)

        result = self.get_event()
        if result is not None:
            return result

        if not any(pygame.mouse.get_pressed(3)[:3] + (pygame.key.get_pressed()[pygame.K_m],)):
            self.drag = (None, 0)

        pos = pygame.mouse.get_pos()
        x, y = self.drawer.convert_coordinates(*pos)
        if 0 <= x < self.drawer.width and 0 <= y < self.drawer.height:
            sprite = self.drawer.grid[y][x]
            if self.drag[1] == "lit" and sprite.lit == self.drag[0]:
                sprite.flip()
            elif self.drag[1] == "mark" and sprite.marked == self.drag[0]:
                sprite.mark()

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
