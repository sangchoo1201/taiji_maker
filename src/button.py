import pygame

import src.const as const


class Button:
    def __init__(self, screen, rect, states=()):
        self.screen = screen
        self.states = states
        self.selected = 0
        self.font = pygame.font.Font("resource/font/D2Coding.ttf", 24)
        self.rect = rect

    def draw(self):
        self.screen.fill(const.GRAY)
        text_image = self.font.render(self.states[self.selected], True, const.WHITE)
        text_rect = text_image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text_image, text_rect)

    def click(self):
        self.selected = (self.selected + 1) % max(1, len(self.states))
