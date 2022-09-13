import pygame

import src.const as const
from src.button import Button
from src.drawer import Drawer
from src.file import reader, writer
from src.palette import Palette
from src.settings import context


class Builder:
    def __init__(self, screen, file_name):
        self.screen = screen
        self.save_path = f"levels/{file_name}"
        self.drawer = Drawer(screen).set_grid(reader(self.save_path))

        self.save_counter = 0

        self.symbol_palette = Palette(250, 26)
        self.symbol_palette.list = [(pygame.image.load(f"resource/symbol/{i}.png"), i) for i in const.SYMBOLS]

        self.color_palette = Palette(250, 0)
        size = context.tile_size
        for color in const.COLORS:
            surface = pygame.Surface((size // 2, size // 2))
            surface.fill(color)
            self.color_palette.list.append((surface, color))

        self.hidden_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.hidden_surface.get_rect(center=(
            context.screen_width // 2 - context.tile_size * 3.1,
            context.screen_height - context.tile_size * 0.8
        ))
        self.hidden_button = Button(self.hidden_surface, rect, ("not hidden", "hidden"))
        self.fixed_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.hidden_surface.get_rect(center=(
            context.screen_width // 2,
            context.screen_height - context.tile_size * 0.8
        ))
        self.fixed_button = Button(self.fixed_surface, rect, ("not fixed", "fixed (not lit)", "fixed (lit)"))
        self.exist_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.hidden_surface.get_rect(center=(
            context.screen_width // 2 + context.tile_size * 3.1,
            context.screen_height - context.tile_size * 0.8
        ))
        self.exist_button = Button(self.exist_surface, rect, ("exist", "not exist"))

        context.is_editing = True

    def get_event(self):
        from main import main, end
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event.button)
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return main
            if event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                writer(self.save_path, self.drawer.grid)
                self.save_counter = 60
            if event.key == pygame.K_UP:
                self.drawer.resize(0, -1)
            if event.key == pygame.K_DOWN:
                self.drawer.resize(0, 1)
            if event.key == pygame.K_LEFT:
                self.drawer.resize(-1, 0)
            if event.key == pygame.K_RIGHT:
                self.drawer.resize(1, 0)

    def handle_mouse(self, mouse_button):
        x, y = pygame.mouse.get_pos()
        for button in (self.hidden_button, self.fixed_button, self.exist_button):
            if button.rect.collidepoint(x, y) and mouse_button == 1:
                button.click()
                return

        if self.symbol_palette.screen.get_rect(topleft=(0, 0)).collidepoint(x, y) and mouse_button == 1:
            i, j = self.symbol_palette.convert_coordinates(x, y)
            if i + j * 3 < len(self.symbol_palette.list):
                self.symbol_palette.selected = i + j * 3
            return

        if self.color_palette.screen.get_rect(topright=(context.screen_width, 0)).collidepoint(x, y) \
                and mouse_button == 1:
            x -= context.screen_width - self.color_palette.width
            i, j = self.color_palette.convert_coordinates(x, y)
            if i + j * 3 < len(self.color_palette.list):
                self.color_palette.selected = i + j * 3
            return

        x, y = self.drawer.convert_coordinates(x, y)
        if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
            return
        sprite = self.drawer.grid[y][x]
        if mouse_button == 3:
            sprite.exist = True
            sprite.hidden = False
            sprite.fixed = False
            sprite.lit = False
            symbol = const.NONE
            color = const.NONE
            sprite.change(symbol, color)
            return
        if mouse_button != 1:
            return

        sprite.hidden = self.hidden_button.selected == 1
        if self.fixed_button.selected == 2:
            sprite.fixed = True
            sprite.lit = True
        elif self.fixed_button.selected == 1:
            sprite.fixed = True
            sprite.lit = False
        else:
            sprite.fixed = False
            sprite.lit = False
        sprite.exist = self.exist_button.selected == 0

        symbol = self.symbol_palette.list[self.symbol_palette.selected][1]
        color = self.color_palette.list[self.color_palette.selected][1]
        if symbol in const.FLOWER or symbol == const.NONE:
            color = const.NONE
        sprite.change(symbol, color)

    def run(self):
        result = self.get_event()
        if result is not None:
            return result

        self.screen.fill(const.DARK)
        self.drawer.draw()
        self.symbol_palette.draw()
        self.screen.blit(
            self.symbol_palette.screen,
            self.symbol_palette.screen.get_rect(topleft=(0, 0))
        )

        self.color_palette.draw()
        self.screen.blit(
            self.color_palette.screen,
            self.color_palette.screen.get_rect(topright=(context.screen_width, 0))
        )

        if self.save_counter > 0:
            self.save_counter -= 1
            font = pygame.font.Font("resource/font/D2Coding.ttf", 48)
            text = font.render("Saved!", True, const.WHITE)
            self.screen.blit(text, text.get_rect(center=(context.screen_width // 2, context.tile_size)))

        for i, button in enumerate((self.hidden_button, self.fixed_button, self.exist_button)):
            button.draw()
            button.rect = button.screen.get_rect(center=(
                context.screen_width // 2 + context.tile_size * (i - 1) * 3.1,
                context.screen_height - context.tile_size * 0.8
            ))
            self.screen.blit(button.screen, button.rect)

        pygame.display.update()
        context.clock.tick(60)
