import json
from tile import Tile


def reader(path):
    with open(path, 'r') as f:
        data = json.load(f)
    for i, row in enumerate(data):
        for j, tile in enumerate(row):
            sprite = Tile()
            sprite.symbol = tile['symbol']
            sprite.color = tuple(tile['color'])
            sprite.fixed = tile['fixed']
            sprite.lit = tile['lit']
            sprite.hidden = tile['hidden']
            sprite.exist = tile['exist']
            sprite.draw()
            data[i][j] = sprite
    return data


def writer(path, data):
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
                "exist": sprite.exist
            }
            data_converted[-1].append(tile)
    with open(path, 'w') as f:
        json.dump(data_converted, f, indent=4)
