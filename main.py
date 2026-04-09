from random import random

width, height = 50,50
world = [[0 for _ in range(width)] for _ in range(height)]

for y in range(height):
    for x in range(width):
        world[y][x] = random()