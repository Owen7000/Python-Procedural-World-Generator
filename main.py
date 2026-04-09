from random import random
from noise import pnoise2
from os import system

system("cls") # All that is needed for windows to allow ANSI codes. I still think it's stupid

width, height = 100, 100
world = [[0 for _ in range(width)] for _ in range(height)]

scale = 20.0

for y in range(height):
    for x in range(width):
        value = pnoise2(x/scale, y/scale)
        world[y][x] = (value + 1) / 2
        
def get_tile_type(value):
    if value < 0.3:
        return "\033[44m \033[0m" # Water
    elif value < 0.6:
        return "\033[42m \033[0m" # Grass
    else:
        return "\033[107m \033[0m" # Mountain
    
for row in world:
    print("".join(get_tile_type(v) for v in row))