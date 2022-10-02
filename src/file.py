import json
import os

from src.tile import Tile
import src.const as const


def reader(path):
    path = path if path.startswith("levels/") or path.startswith("levels\\") else f"levels/{path}"
    if not os.path.exists(path) or path == "levels/":
        return [[Tile() for _ in range(5)] for _ in range(5)]
    with open(path, 'r') as f:
        data = json.load(f)
    for i, row in enumerate(data):
        for j, tile in enumerate(row):
            sprite = Tile()
            sprite.symbol = tile['symbol']
            sprite.color = tuple(tile['color']) if type(tile['color']) == list else tile['color']
            sprite.fixed = tile['fixed']
            sprite.lit = tile['lit']
            sprite.hidden = tile['hidden']
            sprite.exist = tile['exist']
            sprite.connected = tile['connected']
            sprite.marked = False
            data[i][j] = sprite
    return data


def writer(path, data):
    path = path if path.startswith("levels/") or path.startswith("levels\\") else f"levels/{path}"
    path = path.replace("/", "\\")
    paths = path.split("\\")
    for i in range(1, len(paths)):
        dir_path = "\\".join(paths[:i])
        if not os.path.exists(dir_path):
            print(dir_path)
            os.mkdir(dir_path)
    data_converted = []
    for row in data:
        data_converted.append([])
        for sprite in row:
            tile = {
                "symbol": sprite.symbol,
                "color": sprite.color,
                "fixed": sprite.fixed,
                "lit": sprite.lit,
                "hidden": sprite.hidden,
                "exist": sprite.exist,
                "connected": sprite.connected
            }
            data_converted[-1].append(tile)
    with open(path, 'w') as f:
        json.dump(data_converted, f, indent=4)


def encode(data):
    output = f"{len(data[0])}:"
    repeating_zeros = 0
    repeating_eights = 0
    for row in data:
        for sprite in row:
            repeating_zeros, repeating_eights, output = \
                encode_single(sprite, repeating_zeros, repeating_eights, output)
    if repeating_zeros > 2:
        output = output[:-repeating_zeros]
        if repeating_zeros >= 26:
            output += "+Z" * (repeating_zeros // 26)
        if repeating_zeros % 26:
            output += f"+{chr(repeating_zeros % 26 + 64)}"
    if repeating_eights > 2:
        output = output[:-repeating_eights]
        if repeating_eights >= 26:
            output += "-Z" * (repeating_eights // 26)
        if repeating_eights % 26:
            output += f"-{chr(repeating_eights % 26 + 64)}"
    return output


colors = dict(zip(const.COLORS, "roygbpkw"))
colors_reverse = dict(zip("roygbpkw", const.COLORS))


def encode_single(sprite, repeating_zeros, repeating_eights, output):
    connected = (("", "<"), ("^", "/"))[sprite.connected[2]][sprite.connected[0]] if sprite.exist else ""
    symbol = chr(const.SYMBOLS.index(sprite.symbol) + 65) if sprite.symbol else ""
    color = colors[sprite.color] if sprite.color else ""
    option = sprite.fixed * 4 + sprite.lit * 2 + sprite.hidden if sprite.exist else 8
    if not sprite.fixed:
        option &= 0b1101
    if any((symbol, color, connected, (option != 8 and repeating_eights), (option and repeating_zeros))):
        repeat = repeating_zeros + repeating_eights
        if repeat > 2:
            output = output[:-repeat]
            sign = "+" if repeating_zeros else "-"
            if repeat >= 26:
                output += f"{sign}Z" * (repeat // 26)
            if repeat % 26:
                output += f"{sign}{chr(repeat % 26 + 64)}"
        repeating_zeros = 0
        repeating_eights = 0
    if option == 0:
        repeating_zeros += 1
    elif option == 8:
        repeating_eights += 1
    output += f"{connected}{symbol}{color}{option}"
    return repeating_zeros, repeating_eights, output


def decode(data):
    width, data = data.split(":")
    width = int(width)
    data = data.split("+")
    data = data[0] + "".join(map(lambda x: "0" * (ord(x[0]) - 64) + x[1:] if x else x, data[1:]))
    data = data.split("-")
    data = data[0] + "".join(map(lambda x: "8" * (ord(x[0]) - 64) + x[1:] if x else x, data[1:]))
    result = [[]]
    i = 0
    while i < len(data):
        sprite = Tile()
        if data[i] != "0":
            if data[i] in "<^/":
                connected = {"^": (False, True), "<": (True, False), "/": (True, True)}[data[i]]
                sprite.connected[:3:2] = connected
                connect(result, width, connected)
                i += 1
            if 65 <= ord(data[i]) <= 90:
                sprite.symbol = const.SYMBOLS[ord(data[i]) - 65]
                i += 1
            if data[i] in colors_reverse:
                sprite.color = colors_reverse[data[i]]
                i += 1
            option = int(data[i])
            sprite.fixed = option // 4
            sprite.lit = option % 4 // 2
            sprite.hidden = option % 2
            sprite.exist = option != 8
            if not sprite.fixed:
                sprite.lit = 0
        i += 1
        if len(result[-1]) == width:
            result.append([])
        result[-1].append(sprite)
    return result


def connect(grid, width, connected):
    if len(grid[-1]) == width:
        i, j = len(grid), 0
    else:
        i, j = len(grid) - 1, len(grid[-1])

    if connected[0]:
        grid[i][j - 1].connected[1] = True
    if connected[1]:
        grid[i - 1][j].connected[3] = True


def get(data):
    try:
        return decode(data)
    except Exception:
        return [[Tile() for _ in range(5)] for _ in range(5)]
