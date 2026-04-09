from random import random
from noise import pnoise2

width, height = 50, 50
world = [[0 for _ in range(width)] for _ in range(height)]

scale = 20.0

for y in range(height):
    for x in range(width):
        value = pnoise2(x/scale, y/scale)
        world[y][x] = (value + 1) / 2
        
def get_tile_type(value):
    if value < 0.3:
        return "W"
    elif value < 0.6:
        return "G"
    else:
        return "M"
    
for row in world:
    print("".join(get_tile_type(v) for v in row))