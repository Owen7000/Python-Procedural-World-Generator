from random import random
from noise import pnoise2
from PIL import Image
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
    
# for row in world:
#     print("".join(get_tile_type(v) for v in row))

def darken(colour:tuple[int, int, int], factor:float):
    return tuple(min(255, max(0, int(c * factor))) for c in colour)
    
def get_tile_type_for_map(value: float):
    if value < 0.3:
        base = (10, 30, 120) # Water
        t = value / 0.3
    elif value < 0.4:
        base = (70, 130, 180) # Shallow Water
        t = (value - 0.3) / 0.1
    elif value < 0.6:
        base = (50, 160, 60) # Grass
        t = (value - 0.4) / 0.2
    else:
        base = (120, 120, 120) # Mountain
        t = (value - 0.6) / 0.4

    shade = 0.6 + (t * 0.6)
    return darken(base, shade)

def save_map_to_file(world:list[list[int]], width:int, height:int):
    image = Image.new('RGB', (width, height), color=(0,0,0))
    pixels = image.load()
    
    for row_index, row in enumerate(world):
        for column_index, column in enumerate(row):
            # print(column)
            pixels[row_index, column_index] = get_tile_type_for_map(column)
            
    image.save("output.png")
            
save_map_to_file(world, width, height)