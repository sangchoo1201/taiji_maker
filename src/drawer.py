import src.const as const
from src.settings import context
from src.tile import Tile


class Drawer:
    def __init__(self, screen):
        self.screen = screen
        self.width = 0
        self.height = 0
        self.grid = []
        self.lit_color = const.LIT
        self.dark_color = const.GRAY

    def set_grid(self, grid):
        self.grid = grid.copy()
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        return self

    def resize(self, dx, dy):
        if dx < 0 and self.width > 1:
            for row in self.grid:
                row.pop()
            self.width -= 1
        if dx > 0:
            for row in self.grid:
                row.append(Tile())
            self.width += 1
        if dy < 0 and self.height > 1:
            self.grid.pop()
            self.height -= 1
        if dy > 0:
            self.grid.append([Tile() for _ in range(self.width)])
            self.height += 1
        return self

    def draw(self):
        for i, row in enumerate(self.grid):
            for j, sprite in enumerate(row):
                self.draw_tile(j, i, sprite)

    def draw_tile(self, x, y, sprite):
        size = context.tile_size
        x_pos = int(context.screen_width // 2 + (x - (self.width - 1) / 2) * size)
        y_pos = int(context.screen_height // 2 + (y - (self.height - 1) / 2) * size)
        sprite.locate(x_pos, y_pos)
        sprite.draw()
        width, height = len(self.grid[-1]), len(self.grid)
        neighbors = [self.grid[y + dy][x + dx] if height > y + dy >= 0 <= x + dx < width else None
                     for dx, dy in const.DIRECTIONS]
        sprite.corner(neighbors)
        self.screen.blit(sprite.image, sprite.rect)

    def convert_coordinates(self, x, y):
        size = context.tile_size
        left = int(context.screen_width // 2 - self.width / 2 * size)
        bottom = int(context.screen_height // 2 - self.height / 2 * size)
        return (x - left) // size, (y - bottom) // size
