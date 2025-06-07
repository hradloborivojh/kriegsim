"""
Board and Terrain System for kriegsim
"""
from enum import Enum
import random

class TerrainType(Enum):
    PLAINS = "plains"
    HILLS = "hills"
    FOREST = "forest"
    RIVER = "river"

TERRAIN_MODIFIERS = {
    TerrainType.PLAINS: {"defense": 0, "concealment": 0, "movement": 0},
    TerrainType.HILLS: {"defense": 2, "concealment": 0, "movement": 0},
    TerrainType.FOREST: {"defense": 1, "concealment": 2, "movement": 0},
    TerrainType.RIVER: {"defense": 0, "concealment": 0, "movement": -2},
}

class Tile:
    def __init__(self, x, y, terrain=None):
        self.x = x
        self.y = y
        self.terrain = terrain or self.random_terrain()
        self.occupant = None  # For units or control points

    def random_terrain(self):
        # Weighted random terrain generation
        return random.choices(
            [TerrainType.PLAINS, TerrainType.HILLS, TerrainType.FOREST, TerrainType.RIVER],
            weights=[0.5, 0.2, 0.2, 0.1],
        )[0]

    def get_modifiers(self):
        return TERRAIN_MODIFIERS[self.terrain]

class Board:
    def __init__(self, width=15, height=15):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for y in range(height)] for x in range(width)]

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None

    def display(self):
        # Simple text display for debugging
        terrain_symbols = {
            TerrainType.PLAINS: '.',
            TerrainType.HILLS: '^',
            TerrainType.FOREST: '*',
            TerrainType.RIVER: '~',
        }
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                row += terrain_symbols[self.grid[x][y].terrain]
            print(row)
