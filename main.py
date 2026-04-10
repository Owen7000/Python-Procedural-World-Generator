from random import randint
from noise import pnoise2
from PIL import Image
from os import system

system("cls") # All that is needed for windows to allow ANSI codes. I still think it's stupid

width, height = 1000, 1000
world = [[0 for _ in range(width)] for _ in range(height)]

scale = 200.0

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

def distance_to_river(x:int, y:int, rivers, max_dist:int=3):
    for dx in range(-max_dist, max_dist + 1):
        for dy in range(-max_dist, max_dist + 1):
            nx, ny = x + dx, y + dy
            if (nx, ny) in rivers:
                return abs(dx) + abs(dy)
    return None    

def generate_rivers(world, count=30, max_length=300):
    flow_map = {}
    rivers = set()
    
    for _ in range(count):
        # pick a high starting point
        while True:
            x = randint(0, len(world[0]) - 1)
            y = randint(0, len(world) - 1)
            if world[y][x] > 0.65:
                break
        
        for _ in range(max_length):
            rivers.add((x, y))
            flow_map[(x, y)] = flow_map.get((x, y), 0) + 1
            
            # stop at ocean
            if world[y][x] < 0.4:
                break
            
            nx, ny, nh = get_lowest_neighbour(x, y, world)
            
            # If neighbours have rivers, they should combine into one river
            if (nx, ny) in flow_map:
                x, y = nx, ny
                continue
            
            # If there is no downhill space, make a small lake
            if nh >= world[y][x]:
                # create small lake
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        lx, ly = x + dx, y + dy
                        if 0 <= lx < len(world[0]) and 0 <= ly < len(world):
                            rivers.add((lx, ly))
                            flow_map[(lx, ly)] = flow_map.get((lx, ly), 0) + 2
                break
            
            x, y = nx, ny
    
    return rivers, flow_map
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

def save_map_to_file(world:list[list[int]], width:int, height:int, rivers):
    image = Image.new('RGB', (width, height), color=(0,0,0))
    pixels = image.load()
    
    for row_index, row in enumerate(world):
        for column_index, column in enumerate(row):
            x, y = column_index, row_index
            
            if (x, y) in rivers:
                flow = flow_map.get((x, y), 1)
                
                if flow > 6:
                    base_colour = (20, 80, 180)
                elif flow > 3:
                    base_colour = (30, 100, 200)
                else:
                    base_colour = (50, 130, 220)
                    
            else:
                base_colour = get_tile_type_for_map(column)
                
                dist = distance_to_river(x, y, rivers, max_dist=3)
                
                if dist is not None:
                    factor = 1 - (0.1 * (1 - dist / 3))
                    base_colour = darken(base_colour, factor)              
                
            light = get_light(column_index, row_index, world)
            final_colour = apply_lighting(base_colour, light)
            
            pixels[column_index, row_index] = final_colour
            
    image.save("output.png")

rivers, flow_map = generate_rivers(world, count=10)

save_map_to_file(world, width, height, rivers)