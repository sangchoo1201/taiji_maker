import pygame
import clipboard

import src.const as const
from src.button import Button
from src.drawer import Drawer
from src.file import reader, writer, encode
from src.palette import Palette
from src.settings import context
from src.textbox import TextBox
from src.player import Player


class Builder:
    def __init__(self, screen, file_name="", new_file=False):
        context.is_editing = True

        self.screen = screen
        if type(file_name) != str:
            self.save_path = ""
            self.drawer = Drawer(screen).set_grid(file_name)
        else:
            self.save_path = file_name
            self.drawer = Drawer(screen).set_grid(reader(self.save_path))
        for row in self.drawer.grid:
            for sprite in row:
                sprite.draw()
        self.new_file = new_file

        self.save_counter = 0
        self.copy_counter = 0

        self.symbol_palette = Palette(250, 26)
        self.symbol_palette.list = [(pygame.image.load(f"resource/symbol/{i}.png"), i) for i in const.SYMBOLS]

        self.color_palette = Palette(250, 0)
        size = context.tile_size
        for color in const.COLORS:
            surface = pygame.Surface((size // 2, size // 2))
            surface.fill(color)
            self.color_palette.list.append((surface, color))

        self.make_buttons()

    def make_buttons(self):
        self.hidden_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.hidden_surface.get_rect(center=(
            context.screen_width // 2 - context.tile_size * 3.1,
            context.screen_height - context.tile_size * 0.8
        ))
        self.hidden_button = Button(self.hidden_surface, rect, ("not hidden", "hidden"))

        self.fixed_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.fixed_surface.get_rect(center=(
            context.screen_width // 2,
            context.screen_height - context.tile_size * 0.8
        ))
        self.fixed_button = Button(self.fixed_surface, rect, ("not fixed", "fixed (not lit)", "fixed (lit)"))

        self.exist_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.exist_surface.get_rect(center=(
            context.screen_width // 2 + context.tile_size * 3.1,
            context.screen_height - context.tile_size * 0.8
        ))
        self.exist_button = Button(self.exist_surface, rect, ("exist", "not exist"))

        self.save_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.save_surface.get_rect(center=(
            context.screen_width - context.tile_size * 1.8,
            context.tile_size * 0.8
        ))
        self.save_button = Button(self.save_surface, rect, ("save (ctrl+S)", "saved"))

        self.copy_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.copy_surface.get_rect(center=(
            context.screen_width - context.tile_size * 1.8,
            context.tile_size * 1.8
        ))
        self.copy_button = Button(self.copy_surface, rect, ("copy (ctrl+C)", "copied"))

        self.play_surface = pygame.Surface((context.tile_size * 3, context.tile_size))
        rect = self.play_surface.get_rect(center=(
            context.screen_width - context.tile_size * 1.8,
            context.tile_size * 2.8
        ))
        self.play_button = Button(self.play_surface, rect, ("play (ctrl+P)", "playing"))

    def reset_buttons(self):
        self.hidden_button.selected = 0
        self.fixed_button.selected = 0
        self.exist_button.selected = 0

    def get_event(self):
        from main import load, end, main
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event.button)
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return main if self.new_file else load
            if event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.save()
            if event.key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LCTRL]:
                clipboard.copy(encode(self.drawer.grid))
                self.copy_counter = 60
            if event.key == pygame.K_p and pygame.key.get_pressed()[pygame.K_LCTRL]:
                result = self.play()
                if result is not None:
                    return result
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
        for button in (self.hidden_button, self.fixed_button, self.exist_button,
                       self.save_button, self.copy_button, self.play_button):
            if button.rect.collidepoint(x, y) and mouse_button == 1:
                button.click()
                return

        if self.symbol_palette.screen.get_rect(topleft=(0, 0)).collidepoint(x, y) and mouse_button == 1:
            i, j = self.symbol_palette.convert_coordinates(x, y)
            if 0 <= i + j * 3 < len(self.symbol_palette.list) and 0 <= i < 3:
                self.symbol_palette.selected = i + j * 3
                self.reset_buttons()
            return

        if self.color_palette.screen.get_rect(topright=(context.screen_width, 0)).collidepoint(x, y) \
                and mouse_button == 1:
            x -= context.screen_width - self.color_palette.width
            i, j = self.color_palette.convert_coordinates(x, y)
            if 0 <= i + j * 3 < len(self.color_palette.list):
                self.color_palette.selected = i + j * 3
            return

        x, y = self.drawer.convert_coordinates(x, y)
        if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
            return
        sprite = self.drawer.grid[y][x]
        if mouse_button == 3:
            sprite.exist = True
            sprite.hidden = sprite.fixed = sprite.lit = False
            symbol = color = const.NONE
            sprite.change(symbol, color)
            return
        if mouse_button != 1:
            return

        if self.symbol_palette.selected == -1:
            sprite.symbol = sprite.color = const.NONE
            sprite.hidden = self.hidden_button.selected == 1
            sprite.fixed = self.fixed_button.selected > 0
            sprite.lit = self.fixed_button.selected == 2
            sprite.exist = self.exist_button.selected == 0
            sprite.draw()
        elif sprite.exist:
            symbol = self.symbol_palette.get_selection()
            color = self.color_palette.get_selection()
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

        if sum((self.hidden_button.selected, self.fixed_button.selected, self.exist_button.selected)) > 0:
            self.symbol_palette.selected = -1

        if self.save_button.selected == 1:
            self.save_button.selected = 0
            self.save()
            self.save_counter = 60

        if self.copy_button.selected == 1:
            self.copy_button.selected = 0
            clipboard.copy(encode(self.drawer.grid))
            self.copy_counter = 60

        if self.play_button.selected == 1:
            result = self.play()
            if result is not None:
                return result

        if self.save_counter > self.copy_counter:
            self.copy_counter = 0
        else:
            self.save_counter = 0

        if self.save_counter + self.copy_counter > 0:
            if self.save_counter > 0:
                self.save_counter -= 1
            else:
                self.copy_counter -= 1
            font = pygame.font.Font("resource/font/D2Coding.ttf", 48)
            text = font.render("Saved!" if self.save_counter > 0 else "Copied!", True, const.WHITE).convert_alpha()
            text.set_alpha(255 * min(self.save_counter + self.copy_counter, 30) // 30)
            self.screen.blit(text, text.get_rect(center=(context.screen_width // 2, context.tile_size)))

        for i, button in enumerate((self.hidden_button, self.fixed_button, self.exist_button)):
            button.draw()
            button.rect = button.screen.get_rect(center=(
                context.screen_width // 2 + context.tile_size * (i - 1) * 3.1,
                context.screen_height - context.tile_size * 0.8
            ))
            self.screen.blit(button.screen, button.rect)

        for i, button in enumerate((self.save_button, self.copy_button, self.play_button)):
            button.draw()
            button.rect = button.screen.get_rect(center=(
                context.screen_width - context.tile_size * 1.8,
                context.tile_size * (i * 1.1 + 0.8)
            ))
            self.screen.blit(button.screen, button.rect)

        pygame.display.update()
        context.clock.tick(60)

    def get_path(self):
        text_box = TextBox(self.screen, "Enter level name", None, ".tj", True)
        while True:
            result_text_box = text_box.run()
            if result_text_box is not None:
                break
        if type(result_text_box) == tuple:
            self.save_path = result_text_box[1]
        else:
            return result_text_box

    def save(self, counter=60):
        if not self.save_path:
            result = self.get_path()
            if result is not None:
                return result
        writer(self.save_path, self.drawer.grid)
        self.save_counter = counter

    def play(self):
        from main import end
        self.play_button.selected = 0
        self.save(counter=0)
        player = Player(self.screen, self.save_path)
        while True:
            result_main = player.run()
            if result_main == end:
                return result_main
            elif result_main is not None:
                context.is_editing = True
                break
