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

def get_light(x:int, y:int, world:list[list[float]]):
    height = world[y][x]
    
    left = world[y][x-1] if x > 0 else height
    right = world[y][x+1] if x < len(world[0]) - 1 else height
    up = world[y-1][x] if y > 0 else height
    down = world[y+1][x] if y < len(world) - 1 else height 
    
    dx = right - left
    dy = down - up
    
    light = (dx + dy) * 2.5
    return light

def get_lowest_neighbour(x:int, y:int, world:list[list[float]]):    
    neighbours:list[tuple[int, int, float]] = []
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            
            if (dx == 0 and dy == 0):
                continue
            
            if 0 <= nx < len(world[0]) and 0 <= ny < len(world):
                neighbours.append((nx, ny, world[ny][nx]))
                
    return min(neighbours, key=lambda t: t[2])

def apply_lighting(colour:tuple[int, int, int], light:float):
    return tuple(
        min(255, max(0, int(c + light * 255))) for c in colour
    )  
    
def get_tile_type_for_map(value: float):
    if value < 0.3:
        base = (10, 30, 120) # Water
        t = value / 0.3
    elif value < 0.4:
        base = (70, 130, 180) # Shallow Water
        t = (value - 0.3) / 0.1
    elif value < 0.45:
        base =  (194, 178, 128)  # Sand
        t = (value - 0.3) / 0.1
    elif value < 0.6:
        base = (50, 160, 60) # Grass
        t = (value - 0.4) / 0.2
    elif value > 0.75:
        base = (240, 240, 240) # Snow
        t = (value - 0.6) / 0.4
    else:
        base = (120, 120, 120) # Mountain
        t = (value - 0.6) / 0.4
        shade = 0.5 + (t * 0.9)
        return darken(base, shade)

    shade = 0.6 + (t * 0.6)
    return darken(base, shade)

def save_map_to_file(world:list[list[int]], width:int, height:int):
    image = Image.new('RGB', (width, height), color=(0,0,0))
    pixels = image.load()
    
    for row_index, row in enumerate(world):
        for column_index, column in enumerate(row):
            base_colour = get_tile_type_for_map(column)
            light = get_light(column_index, row_index, world)
            final_colour = apply_lighting(base_colour, light)
            
            pixels[column_index, row_index] = final_colour
            
    image.save("output.png")
            
save_map_to_file(world, width, height)