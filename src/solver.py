import itertools
import src.const as const
from collections import deque


class Solver:
    def __init__(self):
        self.solutions = []
        self.remainder = set()
        self.iterations = 0
        self.shapes = {}
        self.shapes_rotate = {}
        self.terminate = True
        self.SOLUTION_LIMIT = 10000

    def bfs(self, x, y):
        queue = deque()
        queue.append((x, y))
        visited = set()
        open_region = False
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
                if self.grid[x + dx][y + dy].lit is None:
                    open_region = True
        return visited, open_region

    def check_flower(self, x, y):
        sprite = self.grid[x][y]
        if sprite.symbol not in const.FLOWER:
            return True
        count = 0
        count_empty = 0
        for dx, dy in const.DIRECTIONS:
            if not 0 <= y + dy < self.width or not 0 <= x + dx < self.height:
                continue
            if not self.grid[x + dx][y + dy].exist:
                continue
            if self.grid[x + dx][y + dy].lit == sprite.lit:
                count += 1
            if self.grid[x + dx][y + dy].lit is None:
                count_empty += 1
        target_count = sprite.symbol - 20
        return False if count > target_count else count + count_empty >= target_count

    def check_diamond(self, area, open_region):
        totals = {}
        diamond_colors = set()
        for x, y in area:
            sprite = self.grid[x][y]
            if sprite.symbol == const.NONE:
                continue
            if sprite.symbol == const.DIAMOND:
                diamond_colors.add(sprite.color)
            if sprite.symbol == const.FLOWER[0]:
                totals[const.PURPLE] = totals.get(const.PURPLE, 0) + 1
            elif sprite.symbol == const.FLOWER[4]:
                totals[const.YELLOW] = totals.get(const.YELLOW, 0) + 1
            elif sprite.symbol in const.FLOWER[1:4]:
                totals[const.PURPLE] = totals.get(const.PURPLE, 0) + 1
                totals[const.YELLOW] = totals.get(const.YELLOW, 0) + 1
            else:
                totals[sprite.color] = totals.get(sprite.color, 0) + 1
        for color in diamond_colors:
            if totals[color] > 2:
                return False
            if not open_region and totals[color] < 2:
                return False
        return True

    def check_dot(self, area, open_region):
        color = None
        dot_count = 0
        extra_count = 0
        neg_count = 0
        x = y = None
        for x, y in area:
            sprite = self.grid[x][y]
            if sprite.symbol == 0 or sprite.symbol > 9:
                continue
            if color is None:
                color = sprite.color
            if color != sprite.color:
                return False
            dot_count += sprite.symbol
            if sprite.symbol < 0:
                neg_count += -sprite.symbol
        if dot_count == 0:
            return True
        if not open_region:
            return dot_count == len(area)
        if len(area) <= dot_count:
            return True
        for x2, y2 in self.remainder:
            sprite = self.grid[x2][y2]
            if sprite.symbol <= 9 and color == sprite.color and self.match_lit(x, y, x2, y2):
                extra_count += sprite.symbol
            if sprite.symbol < 0 and color == sprite.color and self.match_lit(x, y, x2, y2):
                neg_count += -sprite.symbol
        return len(area) < dot_count + extra_count or neg_count >= dot_count

    def match_lit(self, x1, y1, x2, y2):
        if not 0 <= y2 < self.width or not 0 <= x2 < self.height:
            return False
        if not self.grid[x2][y2].exist:
            return False
        if self.grid[x1][y1].lit is None or self.grid[x2][y2].lit is None:
            return None
        return self.grid[x1][y1].lit == self.grid[x2][y2].lit

    def check_match(self, area, x, y, x2, y2):
        if self.grid[x][y].symbol == const.SLASH or self.grid[x2][y2].symbol == const.SLASH:
            return self.check_match_rotated(area, x, y, x2, y2)
        return self.check_match_r0(area, x, y, x2, y2)

    def check_match_r0(self, area, x, y, x2, y2):
        for x3, y3 in area:
            x4, y4 = x3 - x + x2, y3 - y + y2
            if not 0 <= y4 < self.width or not 0 <= x4 < self.height:
                return False
            if not self.grid[x4][y4].exist:
                return False
            for dx, dy in const.DIRECTIONS:
                match = self.match_lit(x3, y3, x3 + dx, y3 + dy)
                if match is None:
                    continue
                match2 = self.match_lit(x4, y4, x4 + dx, y4 + dy)
                if match2 is None:
                    continue
                if match != match2:
                    return False
        return True

    def check_match_r1(self, area, x, y, x2, y2):  # (x, y) -> (-x, -y)
        for x3, y3 in area:
            x4, y4 = x - x3 + x2, y - y3 + y2
            if not 0 <= y4 < self.width or not 0 <= x4 < self.height:
                return False
            if not self.grid[x4][y4].exist:
                return False
            for dx, dy in const.DIRECTIONS:
                match = self.match_lit(x3, y3, x3 + dx, y3 + dy)
                if match is None:
                    continue
                match2 = self.match_lit(x4, y4, x4 - dx, y4 - dy)
                if match2 is None:
                    continue
                if match != match2:
                    return False
        return True

    def check_match_r2(self, area, x, y, x2, y2):  # (x, y) -> (y, -x)
        for x3, y3 in area:
            x4, y4 = y3 - y + x2, x - x3 + y2
            if not 0 <= y4 < self.width or not 0 <= x4 < self.height:
                return False
            if not self.grid[x4][y4].exist:
                return False
            for dx, dy in const.DIRECTIONS:
                match = self.match_lit(x3, y3, x3 + dx, y3 + dy)
                if match is None:
                    continue
                match2 = self.match_lit(x4, y4, x4 + dy, y4 - dx)
                if match2 is None:
                    continue
                if match != match2:
                    return False
        return True

    def check_match_r3(self, area, x, y, x2, y2):  # (x, y) -> (-y, x)
        for x3, y3 in area:
            x4, y4 = y - y3 + x2, x3 - x + y2
            if not 0 <= y4 < self.width or not 0 <= x4 < self.height:
                return False
            if not self.grid[x4][y4].exist:
                return False
            for dx, dy in const.DIRECTIONS:
                match = self.match_lit(x3, y3, x3 + dx, y3 + dy)
                if match is None:
                    continue
                match2 = self.match_lit(x4, y4, x4 - dy, y4 + dx)
                if match2 is None:
                    continue
                if match != match2:
                    return False
        return True

    def check_match_rotated(self, area, x, y, x2, y2):
        return self.check_match_r0(area, x, y, x2, y2) or \
               self.check_match_r1(area, x, y, x2, y2) or \
               self.check_match_r2(area, x, y, x2, y2) or \
               self.check_match_r3(area, x, y, x2, y2)

    def check_line(self, area, open_region):  # sourcery skip: low-code-quality
        for x, y in area:
            sprite = self.grid[x][y]
            # Find matching lines
            if sprite.symbol not in (const.DASH, const.SLASH):
                continue
            for x2, row in enumerate(self.grid):
                for y2, sprite2 in enumerate(row):
                    if x == x2 and y == y2:
                        continue
                    if sprite.color == sprite2.color and \
                            sprite2.symbol in (const.DASH, const.SLASH) and \
                            not self.check_match(area, x, y, x2, y2):
                        return False
            # Check for re-used shapes
            if not open_region and sprite.color not in self.shapes and sprite.color not in self.shapes_rotate:
                rooted_area = {(X - x, Y - y) for X, Y in area}
                for shape in self.shapes.values():
                    if self.is_identical(rooted_area, shape, sprite.symbol == const.SLASH):
                        return False
                for shape in self.shapes_rotate.values():
                    if self.is_identical(rooted_area, shape, True):
                        return False
                if sprite.symbol == const.DASH:
                    self.shapes = dict(self.shapes.items())
                    self.shapes[sprite.color] = rooted_area
                else:
                    self.shapes_rotate = dict(self.shapes_rotate.items())
                    self.shapes_rotate[sprite.color] = rooted_area
            # CHeck just in case the shape was rotated the second time around
            if not open_region and sprite.symbol == const.SLASH and sprite.color not in self.shapes_rotate:
                self.shapes = dict(self.shapes.items())
                shape2 = self.shapes.pop(sprite.color)
                for shape in self.shapes.values():
                    if self.is_identical(shape2, shape, True):
                        return False
                self.shapes_rotate = dict(self.shapes_rotate.items())
                self.shapes_rotate[sprite.color] = shape2
        return True

    def check_connected(self, x: int, y: int) -> bool:
        if (x > 0 and self.grid[x - 1][y].exist and self.grid[x][y].connected[2] is True or
                self.grid[x - 1][y].connected[3] is True) and self.grid[x][y].lit != self.grid[x - 1][y].lit:
            return False
        return (y <= 0 or not self.grid[x][y - 1].exist or self.grid[x][y].connected[0] is not True) and \
            self.grid[x][y - 1].connected[1] is not True or self.grid[x][y].lit == self.grid[x][y - 1].lit

    @staticmethod
    def is_identical(shape1, shape2, can_rotate=False) -> bool:
        if len(shape1) != len(shape2):
            return False
        if shape1 == shape2:
            return True
        return shape1 in [{(y, -x) for x, y in shape2}, {(-y, x) for x, y in shape2}, {(-x, -y) for x, y in shape2}] \
            if can_rotate else False

    def check(self, x: int, y: int) -> bool:
        if not 0 <= y < self.width or not 0 <= x < self.height or not self.grid[x][y].exist:
            return True
        area, open_region = self.bfs(x, y)
        if not self.check_diamond(area, open_region):
            return False
        if not self.check_dot(area, open_region):
            return False
        if not self.check_line(area, open_region):
            return False
        if not open_region:
            self.remainder = self.remainder.copy()
            for point in area:
                self.remainder.discard(point)
        return True

    def check_neighboring(self, x: int, y: int) -> bool:
        if x > 0 and not self.check_flower(x - 1, y):
            return False
        if y > 0 and not self.check_flower(x, y - 1):
            return False
        if not self.check_flower(x, y):
            return False
        if not self.check(x, y):
            return False
        if not self.check_connected(x, y):
            return False
        if x > 0 and self.grid[x][y].lit != self.grid[x - 1][y].lit and not self.check(x - 1, y):
            return False
        return bool(y <= 0 or self.grid[x][y].lit == self.grid[x][y - 1].lit or self.check(x, y - 1))

    def solve(self, grid) -> None:
        self.grid = grid
        self.remainder = set()
        self.iterations = 0
        self.width = len(grid[0])
        self.height = len(grid)
        self.shapes = {}
        self.shapes_rotate = {}
        self.solutions = []
        self.terminate = False
        for x, y in itertools.product(range(self.height), range(self.width)):
            sprite = self.grid[x][y]
            if not sprite.fixed:
                sprite.lit = None
            if sprite.symbol != const.NONE:
                self.remainder.add((x, y))
        result = self.solve_r(0, 0)
        if result is False:
            for x, y in itertools.product(range(self.height), range(self.width)):
                sprite = self.grid[x][y]
                if not sprite.fixed:
                    sprite.lit = False
        self.terminate = True
        self.solve_r(0, 0)

    def solve_r(self, x, y) -> bool:  # sourcery skip: low-code-quality
        if self.terminate and self.solutions:
            sol = self.solutions[0]
            for x in range(len(sol)):
                for y in range(len(sol[0])):
                    self.grid[x][y].lit = sol[x][y]
            return True
        elif self.terminate:
            for x in range(len(self.grid)):
                for y in range(len(self.grid[0])):
                    if not self.grid[x][y].fixed:
                        self.grid[x][y].lit = False
            return True
        self.iterations += 1
        if y >= self.width:
            y = 0
            x += 1
        if x >= self.height:
            sol = [[s.lit for s in row] for row in self.grid]
            self.solutions.append(sol)
            if len(self.solutions) >= self.SOLUTION_LIMIT:
                self.terminate = True
            return False
        sprite = self.grid[x][y]
        if not sprite.exist:
            return self.solve_r(x, y + 1)
        if sprite.fixed:
            return bool(self.check_neighboring(x, y) and self.solve_r(x, y + 1))
        shapes_back = self.shapes
        shapes_rotate_back = self.shapes_rotate
        remainder_back = self.remainder
        sprite.lit = True
        if self.check_neighboring(x, y) and self.solve_r(x, y + 1):
            return True
        self.shapes = shapes_back
        self.shapes_rotate = shapes_rotate_back
        self.remainder = remainder_back
        sprite.lit = False
        if self.check_neighboring(x, y) and self.solve_r(x, y + 1):
            return True
        self.shapes = shapes_back
        self.shapes_rotate = shapes_rotate_back
        self.remainder = remainder_back
        sprite.lit = None
        return False
