import pygame

import src.const as const
from src.settings import context


class Menu:
    def __init__(self, screen):
        from main import make, load, select, play, end
        self.screen = screen
        self.options = (
            ("make new level", make), ("edit level", load),
            ("play level", select), ("from clipboard", play), ("quit", end)
        )
        self.selecting = context.menu
        self.option_font = pygame.font.Font("resource/font/D2Coding.ttf", context.tile_size * 7 // 8)

    def get_event(self):
        from main import end
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEWHEEL:
                self.selecting -= event.y
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue
                self.selecting = max(0, min(len(self.options) - 1, self.selecting))
                context.menu = self.selecting
                return self.options[self.selecting][1]
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return end
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecting -= 1
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecting += 1
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.selecting = max(0, min(len(self.options) - 1, self.selecting))
                context.menu = self.selecting
                return self.options[self.selecting][1]

    def run(self):
        result = self.get_event()
        if result is not None:
            return result

        self.selecting %= len(self.options)

        self.screen.fill(const.DARK)

        for i, line in enumerate(self.options):
            text = f"> {line[0]} <" if i == self.selecting else line[0]
            text_image = self.option_font.render(text, True, const.WHITE)
            text_rect = text_image.get_rect(
                center=(context.screen_width // 2, int((i + 6) * context.tile_size * 9 // 8)))
            self.screen.blit(text_image, text_rect)

        pygame.display.update()
        context.clock.tick(60)
