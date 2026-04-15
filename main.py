from random import randint
from noise import pnoise2
from PIL import Image
from os import system
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import tkinter as tk
from tkinter import ttk

#system("cls") # All that is needed for windows to allow ANSI codes. I still think it's stupid

width, height = 1000, 1000
world = [[0 for _ in range(width)] for _ in range(height)]

scale = 20.0

# setup the world thresholds. I have no intention to actually use these for a while. I'm only adding them in so I can make the GUI
water_level = 0.3
beach_level = 0.35
mountain_level = 0.7
forest_moisture = 0.3
desert_moisture = 0.6

for y in range(height):
    print(f"Generated world row: {y}")
    for x in range(width):
        #system("cls")
        # print(f"Generating world pixel: ({x}, {y})")
        value = pnoise2(x/scale, y/scale)
        world[y][x] = (value + 1) / 2
        
moisture_map = [[0 for _ in range(width)] for _ in range(height)]

moisture_scale = 50.0

for y in range(height):
    print(f"Generated moisture row: {y}")
    for x in range(width):
        #system("cls")
        # print(f"Generating moisture pixel: ({x}, {y})")
        value = pnoise2(x / moisture_scale + 100, y / moisture_scale + 100)
        moisture_map[y][x] = (value + 1) / 2
        
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
    #system("cls")
    print("Generating rivers")
    
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
    
def get_tile_type_for_map(value:float, moisture:float):    
    # if value < 0.3:
    #     base = (10, 30, 120) # Water
    #     t = value / 0.3
    # elif value < 0.4:
    #     base = (70, 130, 180) # Shallow Water
    #     t = (value - 0.3) / 0.1
    # elif value < 0.45:
    #     base =  (194, 178, 128)  # Sand
    #     t = (value - 0.3) / 0.1
    # elif value < 0.6:
    #     base = (50, 160, 60) # Grass
    #     t = (value - 0.4) / 0.2
    # elif value > 0.75:
    #     base = (240, 240, 240) # Snow
    #     t = (value - 0.6) / 0.4
    # else:
    #     base = (120, 120, 120) # Mountain
    #     t = (value - 0.6) / 0.4
    #     shade = 0.5 + (t * 0.9)
    #     return darken(base, shade)
    if value < water_level:
        base = (10, 30, 120) # Water
        t = value / 0.3
    elif value < beach_level:
        base =  (194, 178, 128)  # Sand
        t = (value - 0.3) / 0.1   
    elif value > mountain_level:
        if moisture < 0.5:
            base = (140, 140, 140) # Dry Rock
        else:
            base = (240, 240, 240) # Snow
            
        t = (value - 0.6) / 0.4
        
    else:
        if moisture < desert_moisture:
            base = (210, 180, 60) # Desert
            t = (value - 0.3) / 0.1
        elif moisture < forest_moisture:
            base = (50, 160, 60) # Grassland
            t = (value - 0.4) / 0.2
        else:
            base = (16, 120, 40) # Forest
            t = (value - 0.4) / 0.2

    shade = 0.6 + (t * 0.6)
    return darken(base, shade)

def save_map_to_file(world:list[list[int]], width:int, height:int, rivers):
    image = Image.new('RGB', (width, height), color=(0,0,0))
    pixels = image.load()
    
    total_pixels:int = width * height
    current_pixel:int = 0
    
    print(f"Done: {current_pixel} of {total_pixels}")
    
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
                height_value = world[row_index][column_index]
                moisture_value = moisture_map[row_index][column_index]

                base_colour = get_tile_type_for_map(height_value, moisture_value)
                
                dist = distance_to_river(x, y, rivers, max_dist=3)
                
                if dist is not None:
                    factor = 1 - (0.1 * (1 - dist / 3))
                    base_colour = darken(base_colour, factor)              
                
            light = get_light(column_index, row_index, world)
            final_colour = apply_lighting(base_colour, light)
            
            pixels[column_index, row_index] = final_colour
            
            # #system("cls")
            current_pixel += 1
        
        percentage = round(( current_pixel / total_pixels ) * 100, 2)
        print(f"{percentage}% complete.")

            
    image.save("output.png")

rivers, flow_map = generate_rivers(world, count=10)

save_map_to_file(world, width, height, rivers)

def plot_world_3d(world):
    height = len(world)
    width = len(world[0])
    
    colour_map = []

    for y in range(height):
        row_colours = []
        for x in range(width):
            h = world[y][x]
            m = moisture_map[y][x]
            
            
            if (x, y) in rivers:
                flow = flow_map.get((x, y), 1)
                
                if flow > 6:
                    r, g, b = (20, 80, 180)
                elif flow > 3:
                    r, g, b = (30, 100, 200)
                else:
                    r, g, b = (50, 130, 220)
            else:
                r, g, b = get_tile_type_for_map(h, m)
            
            # matplotlib expects 0–1, not 0–255
            row_colours.append((r/255, g/255, b/255))
        
        colour_map.append(row_colours)

    colour_map = np.array(colour_map)
    
    X, Y = np.meshgrid(range(width), range(height))
    Z = np.array(world)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot_surface(X, Y, Z, facecolors=colour_map, shade=False)
    ax.view_init(elev=45, azim=135)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    
    plt.show()
    
# plot_world_3d(world)

# I'm adding in a GUI, because I'm fedup having to rerun the entire script every time I change a threshold.

root = tk.Tk()
root.title("World Settings")

water_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01,
                        orient="horizontal", label="Water Level")
water_slider.set(0.3)
water_slider.pack()

beach_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", label="Beach Level")
beach_slider.set(0.35)
beach_slider.pack()

mountain_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", label="Mountain Level")
mountain_slider.set(0.7)
mountain_slider.pack()

desert_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", label="Desert Moisture")
desert_slider.set(0.3)
desert_slider.pack()

forest_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", label="Forest Moisture")
forest_slider.set(0.6)
forest_slider.pack()

def redraw_map():
    global water_level, beach_level, mountain_level
    global desert_moisture, forest_moisture

    water_level = water_slider.get()
    beach_level = beach_slider.get()
    mountain_level = mountain_slider.get()

    desert_moisture = desert_slider.get()
    forest_moisture = forest_slider.get()

    save_map_to_file(world, width, height, rivers)
    print("Map redrawn")

redraw_button = tk.Button(root, text="Redraw Map", command=redraw_map)
redraw_button.pack()

root.mainloop()