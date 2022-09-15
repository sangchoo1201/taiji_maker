import pygame

import src.const as const
from src.settings import context


class TextBox:
    def __init__(self, screen, text, callback, suffix="", *args):
        self.screen = screen
        self.text = text
        self.callback = callback
        self.suffix = suffix
        self.font = pygame.font.Font("resource/font/D2Coding.ttf", 64)
        self.input_font = pygame.font.Font("resource/font/D2Coding.ttf", 48)
        self.input = ""
        self.backspace_count = -1
        self.args = args

    def get_input(self):
        from main import end, main, make
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return main
            if event.key == pygame.K_BACKSPACE:
                self.backspace_count = 25
                self.input = self.input[:-1]
            elif event.key == pygame.K_RETURN and self.input.strip():
                self.input = self.input.strip()
                return self.callback, self.input + self.suffix, *self.args
            else:
                self.input += event.unicode
                self.input = self.input.lstrip()[:30]

    def run(self):
        result = self.get_input()
        if result is not None:
            return result

        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.backspace_count -= 1
        else:
            self.backspace_count = -1

        if self.backspace_count == 0:
            self.input = self.input[:-1]
            self.backspace_count = 2

        self.screen.fill(const.BLACK)
        text = self.font.render(self.text, True, const.WHITE)
        text_rect = text.get_rect()
        text_rect.center = self.screen.get_rect().center
        text_rect.y -= context.tile_size // 2
        self.screen.blit(text, text_rect)
        input_text = self.input_font.render(self.input, True, const.WHITE)
        input_rect = input_text.get_rect()
        input_rect.center = self.screen.get_rect().center
        input_rect.y += context.tile_size
        self.screen.blit(input_text, input_rect)

        pygame.display.update()
        context.clock.tick(60)
