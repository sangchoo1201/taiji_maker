import random
from collections import deque

import src.const as const
from src.solver import Solver


class Generator:
    def __init__(self, grid):
        self.grid = grid
        self.solver = Solver()
        self.terminate = True
        self.used_shapes = {}
        self.can_rotate = {}

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
                if not 0 <= y + dy < len(self.grid[0]) or not 0 <= x + dx < len(self.grid):
                    continue
                if not self.grid[x + dx][y + dy].exist:
                    continue
                if self.grid[x + dx][y + dy].lit == self.grid[x][y].lit:
                    queue.append((x + dx, y + dy))
        return visited

    def gen_flowers(self, amount, petal_count=None):
        spaces = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(spaces)
        while amount > 0:
            if not spaces:
                return False
            x, y = spaces.pop()
            sprite = self.grid[x][y]
            if sprite.symbol != 0 or not sprite.exist:
                continue
            count = 0
            for dx, dy in const.DIRECTIONS:
                if not 0 <= y + dy < len(self.grid[0]) or not 0 <= x + dx < len(self.grid):
                    continue
                if not self.grid[x + dx][y + dy].exist:
                    continue
                if self.grid[x + dx][y + dy].lit == sprite.lit:
                    count += 1
            if petal_count is not None and petal_count != count:
                continue
            sprite.symbol = const.FLOWER[count]
            amount -= 1
        return True

    def gen_diamonds(self, color, amount):  # sourcery skip: low-code-quality
        spaces = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(spaces)
        while amount > 0:
            if not spaces:
                return False
            x, y = spaces.pop()
            sprite = self.grid[x][y]
            if sprite.symbol != 0 or not sprite.exist:
                continue
            count = 0
            area = list(self.bfs(x, y))
            random.shuffle(area)
            for x2, y2 in area:
                if (x2, y2) in spaces:
                    spaces.remove((x2, y2))
                sprite2 = self.grid[x2][y2]
                if sprite2.symbol == 0:
                    continue
                if sprite2.symbol in const.FLOWER[1:4] and color in (const.PURPLE, const.YELLOW):
                    count += 1
                elif sprite2.symbol == const.FLOWER[4] and color == const.YELLOW:
                    count += 1
                elif color == sprite2.color:
                    count += 1
            if count == 0 and amount > 1:  # Add another to make a pair
                for x2, y2 in area:
                    if x == x2 and y == y2:
                        continue
                    if (x2, y2) in area and self.grid[x2][y2].symbol == 0 and self.grid[x2][y2].exist:
                        sprite2 = self.grid[x2][y2]
                        sprite.symbol = const.DIAMOND
                        sprite.color = color
                        sprite2.symbol = const.DIAMOND
                        sprite2.color = color
                        amount -= 2
                        break
            elif count == 1:
                sprite.symbol = const.DIAMOND
                sprite.color = color
                amount -= 1
        return True

    def gen_dots(self, color, amount, dot_count=None):  # sourcery skip: low-code-quality
        spaces = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        neg_spaces = [(x, y) for x, y in spaces if self.grid[x][y].symbol in const.DOT[-9:]]
        random.shuffle(spaces)
        random.shuffle(neg_spaces)
        while amount > 0:
            if not spaces:
                return False
            x, y = neg_spaces.pop() if neg_spaces else spaces.pop()
            area = self.bfs(x, y)
            area_open = []
            fail_on_color = False
            neg_count = 0
            for x2, y2 in area:
                if self.grid[x2][y2].symbol == 0 and self.grid[x2][y2].exist:
                    area_open.append((x2, y2))
                elif self.grid[x2][y2].symbol in const.DOT and self.grid[x2][y2].color != color:
                    fail_on_color = True
                elif self.grid[x2][y2].symbol in const.DOT[-9:]:
                    neg_count += -self.grid[x2][y2].symbol
                if (x2, y2) in spaces:
                    spaces.remove((x2, y2))
                if (x2, y2) in neg_spaces:
                    neg_spaces.remove((x2, y2))
            if fail_on_color or not area_open:
                continue
            if dot_count and (len(area) % dot_count != 0 or len(area) // dot_count > min(amount, len(area_open))):
                continue
            count = len(area) + neg_count
            if neg_count > 0 and random.randrange(5) == 0:
                count = neg_count  # Build a canceling region
            while count > 0:
                selected_count = min(random.randrange(1, 15), count, 9)
                if dot_count:
                    selected_count = dot_count
                elif amount == 1 or len(area_open) == 1:
                    if count > 9:
                        if count <= len(area) or count - len(area) > 9 or count <= neg_count:
                            return False
                        selected_count = count - len(area)  # Build a canceling region
                        count = 0
                    else:
                        selected_count = count
                x2, y2 = area_open.pop()
                self.grid[x2][y2].symbol = const.DOT[selected_count]
                self.grid[x2][y2].color = color
                count -= selected_count
                amount -= 1
        return not neg_spaces

    def gen_antidots(self, color, amount, dot_count=None):
        spaces = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(spaces)
        while amount > 0:
            if not spaces:
                return False
            x, y = spaces.pop()
            sprite = self.grid[x][y]
            if sprite.symbol != 0:
                continue
            area = self.bfs(x, y)
            area_open = []
            fail_on_color = False
            for x2, y2 in area:
                if self.grid[x2][y2].symbol == 0 and self.grid[x2][y2].exist:
                    area_open.append((x2, y2))
                elif self.grid[x2][y2].symbol in const.DOT and self.grid[x2][y2].color != color:
                    fail_on_color = True
            if fail_on_color or len(area_open) <= 1:
                continue
            selected_count = min(random.randrange(1, 7), random.randrange(1, 7))
            if dot_count:
                selected_count = dot_count
            self.grid[x][y].symbol = const.DOT[-selected_count]
            self.grid[x][y].color = color
            amount -= 1
        return True

    def gen_lines(self, color, amount, num_rotated):  # sourcery skip: low-code-quality
        shape = set()
        self.can_rotate[color] = (num_rotated > 0)
        while not shape or any(
                self.is_identical(shape, s, num_rotated > 0 or self.can_rotate[c])
                for c, s in self.used_shapes.items()
        ):
            shape = {(0, 0)}
            shape_size = random.choice([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 9])
            while len(shape) < shape_size:
                x, y = random.choice(list(shape))
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                x2, y2 = x + dx, y + dy
                shape.add((x2, y2))
        rotations = [
            shape,
            {(y, -x) for x, y in shape},
            {(-x, -y) for x, y in shape},
            {(-y, x) for x, y in shape}
        ]
        spaces = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(spaces)
        previous = None
        while amount > 0:
            if not spaces:
                return False
            x, y = spaces.pop()
            if self.grid[x][y].symbol != 0 or not self.grid[x][y].exist:
                continue
            if amount <= num_rotated:
                shape = random.choice(rotations)
            placed_shape = set()
            placed_shape_border = set()
            for x2, y2 in shape:
                x3, y3 = x + x2, y + y2
                if 0 <= x3 < len(self.grid) and 0 <= y3 < len(self.grid[0]):
                    placed_shape.add((x3, y3))
                else:
                    break
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if 0 <= x3 + dx < len(self.grid) and 0 <= y3 + dy < len(self.grid[0]):
                        placed_shape_border.add((x3 + dx, y3 + dy))
            if len(shape) != len(placed_shape):
                continue
            placed_shape_border = placed_shape_border.difference(placed_shape)
            lit_choices = []
            if self.check_shape_placement(placed_shape, placed_shape_border, True):
                lit_choices.append(True)
            if self.check_shape_placement(placed_shape, placed_shape_border, False):
                lit_choices.append(False)
            if random.randrange(2) == 0 and previous in lit_choices:
                lit_choices.remove(previous)
            if not lit_choices:
                continue
            lit = random.choice(lit_choices)
            previous = lit
            for x2, y2 in placed_shape:
                if not self.propagate_lit(x2, y2, lit):
                    return False
            for x2, y2 in placed_shape_border:
                if not self.propagate_lit(x2, y2, not lit):
                    return False
            self.grid[x][y].symbol = const.SLASH if amount <= num_rotated else const.DASH
            self.grid[x][y].color = color
            amount -= 1
            num_rotated = min(num_rotated, amount)
        self.used_shapes[color] = shape
        return True

    def check_shape_placement(self, placed_shape, placed_shape_border, lit):
        for x, y in placed_shape:
            sprite = self.grid[x][y]
            if not sprite.exist:
                return False
            for dx, dy in const.DIRECTIONS:
                if self.is_connected(x, y, x + dx, y + dy) and (x + dx, y + dy) not in placed_shape:
                    return False
            if sprite.lit is None:
                continue
            if sprite.lit != lit:
                return False
        for x, y in placed_shape_border:
            sprite = self.grid[x][y]
            for dx, dy in const.DIRECTIONS:
                if self.is_connected(x, y, x + dx, y + dy) and self.grid[x + dx][y + dy].lit is not None and \
                        self.grid[x + dx][y + dy].lit == lit:
                    return False
            if sprite.lit is None:
                continue
            if sprite.lit == lit:
                return False
        return True

    def is_connected(self, x, y, x2, y2):
        if x2 < 0 or x2 >= len(self.grid) or y2 < 0 or y2 >= len(self.grid[0]):
            return False
        if x == x2 and y < y2:
            return self.grid[x][y].connected[1] or self.grid[x2][y2].connected[0]
        if x == x2 and y > y2:
            return self.grid[x][y].connected[0] or self.grid[x2][y2].connected[1]
        if y == y2 and x < x2:
            return self.grid[x][y].connected[3] or self.grid[x2][y2].connected[2]
        if y == y2 and x > x2:
            return self.grid[x][y].connected[2] or self.grid[x2][y2].connected[3]

    def propagate_lit(self, x, y, lit):
        if x < 0 or x >= len(self.grid) or y < 0 or y >= len(self.grid[0]):
            return True
        sprite = self.grid[x][y]
        if sprite.lit == lit:
            return True
        if sprite.lit == (not lit):
            return False
        sprite.lit = lit
        return (not self.is_connected(x, y, x + 1, y) or self.propagate_lit(x + 1, y, lit)) and \
               (not self.is_connected(x, y, x - 1, y) or self.propagate_lit(x - 1, y, lit)) and \
               (not self.is_connected(x, y, x, y + 1) or self.propagate_lit(x, y + 1, lit)) and \
               (not self.is_connected(x, y, x, y - 1) or self.propagate_lit(x, y - 1, lit))

    def propagate_fixed(self, x, y):
        if x < 0 or x >= len(self.grid) or y < 0 or y >= len(self.grid[0]):
            return True
        sprite = self.grid[x][y]
        if sprite.fixed:
            return True
        sprite.fixed = True
        return (not self.is_connected(x, y, x + 1, y) or self.propagate_fixed(x + 1, y)) and \
               (not self.is_connected(x, y, x - 1, y) or self.propagate_fixed(x - 1, y)) and \
               (not self.is_connected(x, y, x, y + 1) or self.propagate_fixed(x, y + 1)) and \
               (not self.is_connected(x, y, x, y - 1) or self.propagate_fixed(x, y - 1))

    @staticmethod
    def is_identical(shape1, shape2, can_rotate=False) -> bool:
        if len(shape1) != len(shape2):
            return False
        if shape1 == shape2:
            return True
        return shape1 in [{(y, -x) for x, y in shape2}, {(-y, x) for x, y in shape2}, {(-x, -y) for x, y in shape2}] \
            if can_rotate else False

    def gen_all_symbols(self, symbols):
        for color, amount in symbols['LINE'].items():
            amountr = symbols['LINE_ROTATED'][color]
            if not self.gen_lines(color, amount + amountr, amountr):
                return False
        # Populate random tiles
        for x, row in enumerate(self.grid):
            for y, sprite in enumerate(row):
                if sprite.lit is None and not self.propagate_lit(x, y, random.choice([True, False])):
                    return False
        for color, amount in symbols['ANTIDOT'].items():
            if not self.gen_antidots(color, amount):
                return False
        for color, amount in symbols['DOT'].items():
            if not self.gen_dots(color, amount):
                return False
        if not self.gen_flowers(symbols['FLOWER']):
            return False
        for color, amount in symbols['DIAMOND'].items():
            if not self.gen_diamonds(color, amount):
                return False
        spaces = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(spaces)
        for x, y in spaces[:symbols['FIXED']]:
            if self.grid[x][y].fixed:
                continue
            self.propagate_fixed(x, y)
        return True

    def generate(self, symbols=None):
        if not symbols:
            symbols = {'DIAMOND': {}, 'FLOWER': 0, 'DOT': {}, 'ANTIDOT': {}, 'LINE': {}, 'LINE_ROTATED': {}, 'FIXED': 0}
            for row in self.grid:
                for sprite in row:
                    if sprite.symbol == const.DIAMOND:
                        symbols['DIAMOND'].setdefault(sprite.color, 0)
                        symbols['DIAMOND'][sprite.color] += 1
                    if sprite.symbol in const.FLOWER:
                        symbols['FLOWER'] += 1
                    if sprite.symbol in const.DOT[1:10]:
                        symbols['DOT'].setdefault(sprite.color, 0)
                        symbols['DOT'][sprite.color] += 1
                    if sprite.symbol in const.DOT[-9:]:
                        symbols['DOT'].setdefault(sprite.color, 0)
                        symbols['ANTIDOT'].setdefault(sprite.color, 0)
                        symbols['ANTIDOT'][sprite.color] += 1
                    if sprite.symbol == const.DASH:
                        symbols['LINE'].setdefault(sprite.color, 0)
                        symbols['LINE_ROTATED'].setdefault(sprite.color, 0)
                        symbols['LINE'][sprite.color] += 1
                    if sprite.symbol == const.SLASH:
                        symbols['LINE'].setdefault(sprite.color, 0)
                        symbols['LINE_ROTATED'].setdefault(sprite.color, 0)
                        symbols['LINE_ROTATED'][sprite.color] += 1
                    if sprite.fixed:
                        symbols['FIXED'] += 1
        self.terminate = False
        self.used_shapes = {}
        self.can_rotate = {}
        while True:
            for row in self.grid:
                for sprite in row:
                    sprite.fixed = False
                    sprite.symbol = sprite.color = 0
                    sprite.lit = None
            if self.gen_all_symbols(symbols) or self.terminate:
                for row in self.grid:
                    for sprite in row:
                        if not sprite.fixed:
                            sprite.lit = False
                self.terminate = True
                return
            # TODO: Implement solution count enforcement
