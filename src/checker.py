import const
from collections import deque


class Checker:
    def __init__(self, grid):
        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)

    def check(self):
        areas = self.divide_areas()
        for area in areas:
            if not self.check_diamond(area):
                return False
            if not self.check_dot(area):
                return False
        return self.check_line(areas) if self.check_flower() else False

    def divide_areas(self):
        already_visited = set()
        areas = []
        for x, row in enumerate(self.grid):
            for y, sprite in enumerate(row):
                if (x, y) in already_visited:
                    continue
                if not sprite.exist:
                    continue
                area = self.bfs(x, y)
                already_visited |= area
                areas.append(area)
        return areas

    def bfs(self, x, y):
        queue = deque()
        queue.append((x, y))
        visited = set()
        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            for dx, dy in const.DIRECTIONS:
                if not 0 <= y + dy < self.width or not 0 <= x + dx < self.height:
                    continue
                if not self.grid[x + dx][y + dy].exist:
                    continue
                if self.grid[x + dx][y + dy].lit == self.grid[x][y].lit:
                    queue.append((x + dx, y + dy))
        return visited

    def check_flower(self):
        for x, row in enumerate(self.grid):
            for y, sprite in enumerate(row):
                count = 0
                if sprite.symbol not in const.FLOWER:
                    continue
                for dx, dy in const.DIRECTIONS:
                    if not 0 <= y + dy < self.width or not 0 <= x + dx < self.height:
                        continue
                    if self.grid[x + dx][y + dy].lit == sprite.lit:
                        count += 1
                if count != sprite.symbol - 20:
                    return False
        return True

    def check_diamond(self, area):
        amounts_diamond = {}
        amounts_other = {}
        for x, y in area:
            sprite = self.grid[x][y]
            if not sprite.exist:
                continue
            if sprite.symbol == const.DIAMOND:
                amounts_diamond[sprite.color] = amounts_diamond.get(sprite.color, 0) + 1
            elif sprite.symbol in const.FLOWER:
                if sprite.symbol != 24:
                    amounts_other[const.PURPLE] = amounts_other.get(const.PURPLE, 0) + 1
                if sprite.symbol != 20:
                    amounts_other[const.YELLOW] = amounts_other.get(const.YELLOW, 0) + 1
            elif sprite.symbol != const.NONE:
                amounts_other[sprite.color] = amounts_other.get(sprite.color, 0) + 1
        for color, amount in amounts_diamond.items():
            if amount == 0:
                continue
            if amount + amounts_other.get(color, 0) != 2:
                return False
        return True

    def check_dot(self, area):
        color = None
        dot_count = 0
        for x, y in area:
            sprite = self.grid[x][y]
            if sprite.symbol not in const.DOT[1:] or not sprite.exist:
                continue
            if color is None:
                color = sprite.color
            if color != sprite.color:
                return False
            dot_count += sprite.symbol
        return dot_count in (0, len(area))

    def check_line(self, areas):  # sourcery skip: dict-assign-update-to-union
        shapes = {}
        shapes_rotate = {}
        for area in areas:
            self.get_line(area, shapes, shapes_rotate)
        colors = set(shapes.keys()) | set(shapes_rotate.keys())
        for color in colors:
            blocks = shapes.get(color, [])
            blocks_rotate = shapes_rotate.get(color, [])
            if len(blocks) + len(blocks_rotate) < 2:
                continue
            standard = blocks[0] if blocks else blocks_rotate[0]
            for block in blocks:
                if not self.is_identical(standard, block):
                    return False
            for block in blocks_rotate:
                if not self.is_identical(standard, block, True):
                    return False
        return True

    def get_line(self, area, shapes, shapes_rotate):
        for x, y in area:
            sprite = self.grid[x][y]
            if not sprite.exist:
                continue
            if sprite.symbol not in (const.DASH, const.SLASH):
                continue
            shape = {(i - x, j - y) for i, j in area}
            target = shapes if sprite.symbol == const.DASH else shapes_rotate
            target[sprite.color] = target.get(sprite.color, []) + [shape]

    def is_identical(self, shape1, shape2, can_rotate=False):
        shape_list = self.rotate(shape2) if can_rotate else (shape2,)
        return any(shape1 == shape for shape in shape_list)

    @staticmethod
    def rotate(shape):
        return shape, {(-y, x) for x, y in shape}, {(-x, -y) for x, y in shape}, {(y, -x) for x, y in shape}
