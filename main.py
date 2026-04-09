from random import random

width, height = 50, 50
world = [[0 for _ in range(width)] for _ in range(height)]

for y in range(height):
    for x in range(width):
        world[y][x] = random()
        
def get_tile_type(value):
    if value < 0.3:
        return "W"
    elif value < 0.6:
        return "G"
    else:
        return "M"
    
for row in world:
    print("".join(get_tile_type(v) for v in row))