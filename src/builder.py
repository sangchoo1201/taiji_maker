import pygame
import clipboard

import itertools
import src.const as const
from src.button import Button
from src.drawer import Drawer
from src.file import reader, writer, encode
from src.palette import Palette
from src.settings import context
from src.textbox import TextBox
from src.player import Player
from src.solver import Solver
import threading


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

        self.solver = Solver()

        self.sol_index = 0

        self.make_buttons()

    def make_buttons(self):
        size = (3 * context.tile_size, context.tile_size)
        rect = pygame.Rect(0, 0, *size)

        self.hidden_surface = pygame.Surface(size)
        self.hidden_button = Button(self.hidden_surface, rect, ("not hidden", "hidden"))

        self.fixed_surface = pygame.Surface(size)
        self.fixed_button = Button(self.fixed_surface, rect, ("not fixed", "fixed (not lit)", "fixed (lit)"))

        self.exist_surface = pygame.Surface(size)
        self.exist_button = Button(self.exist_surface, rect, ("exist", "not exist"))

        self.save_surface = pygame.Surface(size)
        self.save_button = Button(self.save_surface, rect, ("save (ctrl+S)", "saved"))

        self.copy_surface = pygame.Surface(size)
        self.copy_button = Button(self.copy_surface, rect, ("copy (ctrl+C)", "copied"))

        self.play_surface = pygame.Surface(size)
        self.play_button = Button(self.play_surface, rect, ("play (ctrl+P)", "playing"))

        self.solve_surface = pygame.Surface(size)
        self.solve_button = Button(self.solve_surface, rect, ("solve", "solving"))

        rect_sq = pygame.Rect(0, 0, context.tile_size, context.tile_size)
        
        self.scroll_surface_l = pygame.Surface((context.tile_size, context.tile_size))
        self.scroll_button_l = Button(self.scroll_surface_l, rect_sq, ("<", "<"))

        self.scroll_surface_r = pygame.Surface((context.tile_size, context.tile_size))
        self.scroll_button_r = Button(self.scroll_surface_r, rect_sq, (">", ">"))

    def reset_buttons(self):
        self.hidden_button.selected = 0
        self.fixed_button.selected = 0
        self.exist_button.selected = 0
        self.solve_button.selected = 0

    def get_event(self):
        from main import load, end, main
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return end
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event.button)
                self.click_tile(event.button, True)
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
            directions = {pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)}
            if event.key in directions:
                self.drawer.resize(*directions[event.key])
                self.solver.solutions = []
                self.solver.terminate = True

    def handle_mouse(self, mouse_button):
        x, y = pygame.mouse.get_pos()
        for button in (self.hidden_button, self.fixed_button, self.exist_button,
                       self.save_button, self.copy_button, self.play_button,
                       self.solve_button, self.scroll_button_l, self.scroll_button_r):
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

    def click_tile(self, mouse_button, button_down=False):  # sourcery skip: low-code-quality
        x, y = self.drawer.convert_coordinates(*pygame.mouse.get_pos())
        if x < 0 or x >= self.drawer.width or y < 0 or y >= self.drawer.height:
            return
        self.solver.solutions = []
        self.solver.terminate = True
        for x2, y2 in itertools.product(range(self.drawer.height), range(self.drawer.width)):
            sprite = self.drawer.grid[x2][y2]
            if not sprite.fixed:
                sprite.lit = False
        sprite = self.drawer.grid[y][x]
        if mouse_button == 3:
            sprite.exist = True
            sprite.hidden = False
            symbol = color = const.NONE
            sprite.change(symbol, color)
            self.visit(x, y)
            return
        if mouse_button != 1:
            return
        connect_map = {pygame.K_a: (-1, 0), pygame.K_d: (1, 0), pygame.K_w: (0, -1), pygame.K_s: (0, 1)}

        if any(pygame.key.get_pressed()[key] for key in connect_map) and button_down:
            for key, (dx, dy) in connect_map.items():
                if pygame.key.get_pressed()[key]:
                    self.connect(x, y, dx, dy)
            return
        if self.symbol_palette.selected == -1:
            sprite.exist = self.exist_button.selected == 0
            if sprite.exist:
                sprite.hidden = self.hidden_button.selected == 1 and sprite.symbol
                sprite.fixed = self.fixed_button.selected > 0
                sprite.lit = self.fixed_button.selected == 2
            else:
                sprite.symbol = sprite.color = const.NONE
                sprite.hidden = sprite.fixed = sprite.lit = False
            self.visit(x, y)
        elif sprite.exist:
            symbol = self.symbol_palette.get_selection()
            color = self.color_palette.get_selection()
            if symbol in const.FLOWER or symbol == const.NONE:
                color = const.NONE
            sprite.change(symbol, color)

    def connect(self, x, y, dx, dy, cut=False):
        width, height = self.drawer.width, self.drawer.height
        sprite = self.drawer.grid[y][x]
        if not sprite.exist:
            return
        direction_number = const.DIRECTIONS.index((dx, dy))
        if not (0 <= x + dx < width and 0 <= y + dy < height):
            return
        other = self.drawer.grid[y + dy][x + dx]
        if sprite.connected[direction_number] and other.connected[direction_number ^ 1] or cut:
            sprite.connected[direction_number] = other.connected[direction_number ^ 1] = False
            return
        other.exist = True
        other.fixed = sprite.fixed
        other.lit = sprite.lit
        sprite.connected[direction_number] = other.connected[direction_number ^ 1] = True

    def visit(self, x, y, visited=None):
        sprite = self.drawer.grid[y][x]
        if visited is None:
            visited = set()
        for dx, dy in (j for i, j in enumerate(const.DIRECTIONS) if sprite.connected[i]):
            if not 0 <= x + dx < self.drawer.width or not 0 <= y + dy < self.drawer.height:
                continue
            if (x + dx, y + dy) not in visited:
                visited.add((x + dx, y + dy))
                other = self.drawer.grid[y + dy][x + dx]
                other.exist = sprite.exist
                other.fixed = sprite.fixed
                other.lit = sprite.lit
                self.visit(x + dx, y + dy, visited)

    def run(self):  # sourcery skip: low-code-quality
        result = self.get_event()
        if result is not None:
            return result

        self.screen.fill(const.DARK)
        self.drawer.draw()
        self.symbol_palette.draw()
        rect = self.symbol_palette.screen.get_rect(topleft=(0, 0))
        self.screen.blit(self.symbol_palette.screen, rect)

        self.color_palette.draw()
        rect = self.color_palette.screen.get_rect(topright=(context.screen_width, 0))
        self.screen.blit(self.color_palette.screen, rect)

        if pygame.mouse.get_pressed()[0]:
            self.click_tile(1)
        if pygame.mouse.get_pressed()[2]:
            self.click_tile(3)

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

        if self.solve_button.selected == 1:
            if self.solver.terminate:
                thread = threading.Thread(target=lambda: self.solver.solve(self.drawer.grid))
                thread.start()
                self.sol_index = 0
            else:
                self.solver.terminate = True
            self.solve_button.selected = 0

        if self.scroll_button_l.selected == 1 or self.scroll_button_r.selected == 1:
            self.sol_index += 1 if self.scroll_button_r.selected == 1 else -1
            self.scroll_button_l = self.scroll_button_r = 0
            if 0 <= self.sol_index < len(self.solver.solutions) and self.solver.terminate:
                self.sol_index -= 1
                sol = self.solver.solutions[self.sol_index]
                for x, y in itertools.product(range(len(sol)), range(len(sol[0]))):
                    self.drawer.grid[x][y].lit = sol[x][y]
            else:
                self.sol_index = max(0, min(self.sol_index, len(self.solver.solutions) - 1))

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

        font = pygame.font.Font("resource/font/D2Coding.ttf", 24)
        text = font.render("W/A/S/D + Left Click:", True, const.WHITE)
        rect = text.get_rect(topleft=(context.tile_size // 2, context.tile_size // 2))
        self.screen.blit(text, rect)

        text = font.render("connect tiles (make big tile)", True, const.WHITE)
        rect = text.get_rect(topleft=(context.tile_size // 2, context.tile_size))
        self.screen.blit(text, rect)

        for i, button in enumerate((self.hidden_button, self.fixed_button, self.exist_button, self.solve_button)):
            button.draw()
            x = context.screen_width // 2 + context.tile_size * (i - 2) * 3.1
            y = context.screen_height - context.tile_size * 0.8
            button.rect = button.screen.get_rect(center=(x, y))

            self.screen.blit(button.screen, button.rect)

        for i, button in enumerate((self.save_button, self.copy_button, self.play_button)):
            button.draw()
            x = context.screen_width - context.tile_size * 1.8
            y = context.screen_height - context.tile_size * (i * 1.1 + 0.8)
            button.rect = button.screen.get_rect(center=(x, y))

            self.screen.blit(button.screen, button.rect)

        if self.solver.solutions and self.solver.terminate:
            if self.sol_index > 0:
                button = self.scroll_button_l
                button.draw()
                x = context.screen_width // 2 - context.tile_size * 4.5 * 1.2
                y = context.screen_height - context.tile_size * 0.8
                button.rect = button.screen.get_rect(center=(x, y))

                self.screen.blit(button.screen, button.rect)
            if self.sol_index < len(self.solver.solutions) - 1:
                button = self.scroll_button_r
                button.draw()
                x = context.screen_width // 2 + context.tile_size * 5.5 * 1.2
                y = context.screen_height - context.tile_size * 0.8
                button.rect = button.screen.get_rect(center=(x, y))

                self.screen.blit(button.screen, button.rect)

        font = pygame.font.Font("resource/font/D2Coding.ttf", 24)
        text = font.render(f"{str(self.sol_index + 1)}/{len(self.solver.solutions)}", True, const.WHITE)
        x = context.screen_width - context.tile_size * 2.2
        y = context.screen_height - context.tile_size * 2.2
        self.screen.blit(text, text.get_rect(topleft=(x, y)))
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
