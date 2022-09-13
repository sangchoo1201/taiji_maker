import glob

import pygame

from src.settings import context
import src.const as const


class Selector:
    def __init__(self, screen, next_scene):
        self.screen = screen
        self.next_scene = next_scene
        self.levels = [f.split("\\")[-1] for f in glob.glob("levels/*.json")]
        self.selecting = context.selecting
        self.bias = 0
        self.font = pygame.font.Font("resource/font/D2Coding.ttf", 48)
        self.up_counter = -1
        self.down_counter = -1

    def get_event(self):
        from main import end, main
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEWHEEL:
                self.selecting -= event.y
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue
                self.selecting = max(0, min(len(self.levels) - 1, self.selecting))
                context.selecting = self.selecting
                return self.next_scene, self.levels[self.selecting]
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return main
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecting -= 1
                self.up_counter = 15
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecting += 1
                self.down_counter = 15
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.selecting = max(0, min(len(self.levels) - 1, self.selecting))
                context.selecting = self.selecting
                return self.next_scene, self.levels[self.selecting]

    def run(self):
        result = self.get_event()
        if result is not None:
            return result

        keys = pygame.key.get_pressed()
        key_up = keys[pygame.K_UP] or keys[pygame.K_w]
        key_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        if key_up and key_down:
            self.up_counter = self.down_counter = -1
        if not key_up:
            self.up_counter = -1
        if not key_down:
            self.down_counter = -1

        if self.up_counter > 0:
            self.up_counter -= 1
        elif self.up_counter == 0:
            self.selecting -= 1
            self.up_counter = 2

        if self.down_counter > 0:
            self.down_counter -= 1
        elif self.down_counter == 0:
            self.selecting += 1
            self.down_counter = 2

        self.selecting = max(0, min(len(self.levels) - 1, self.selecting))
        max_levels = int(context.screen_height / 64 - 0.51)
        if self.selecting < self.bias:
            self.bias = self.selecting
        elif self.selecting >= self.bias + max_levels:
            self.bias = self.selecting - max_levels + 1

        self.screen.fill(const.DARK)

        for i, line in enumerate(self.levels[self.bias:self.bias + max_levels]):
            if i + self.bias == self.selecting:
                text_image = self.font.render(">", True, const.WHITE)
                text_rect = text_image.get_rect(bottomleft=(32, int((i + 1.5) * 64)))
                self.screen.blit(text_image, text_rect)
                line = f" {line}"
            text_image = self.font.render(line[:-5], True, const.WHITE)
            text_rect = text_image.get_rect(bottomleft=(80, int((i + 1.5) * 64)))
            self.screen.blit(text_image, text_rect)

        pygame.display.update()
        context.clock.tick(60)
