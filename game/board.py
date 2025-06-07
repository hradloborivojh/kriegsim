"""
Board and Terrain System for kriegsim
Enhanced for tactical war simulation with neural network learning
"""
from enum import Enum
import random
import pygame

class TerrainType(Enum):
    FLAT = "flat"
    HIGH_GROUND = "high_ground"
    LOW_GROUND = "low_ground"
    TRENCHES = "trenches"

# Color coding for visual representation
TERRAIN_COLORS = {
    TerrainType.FLAT: (144, 238, 144),        # Light green
    TerrainType.HIGH_GROUND: (139, 69, 19),   # Saddle brown
    TerrainType.LOW_GROUND: (70, 130, 180),   # Steel blue
    TerrainType.TRENCHES: (105, 105, 105),    # Dim gray
}

TERRAIN_MODIFIERS = {
    TerrainType.FLAT: {"defense": 0, "range_bonus": 0, "movement": 0},
    TerrainType.HIGH_GROUND: {"defense": 0, "range_bonus": 1, "movement": 0},
    TerrainType.LOW_GROUND: {"defense": -1, "range_bonus": 0, "movement": 0},
    TerrainType.TRENCHES: {"defense": 1, "range_bonus": 0, "movement": 0},
}

class Tile:
    def __init__(self, x, y, terrain=None):
        self.x = x
        self.y = y
        self.terrain = terrain or self.random_terrain()
        self.occupant = None  # For units
        self.pending_attacks = []  # For delayed attacks (mortars)

    def random_terrain(self):
        # Weighted random terrain generation
        return random.choices(
            [TerrainType.FLAT, TerrainType.HIGH_GROUND, TerrainType.LOW_GROUND, TerrainType.TRENCHES],
            weights=[0.4, 0.2, 0.2, 0.2],
        )[0]

    def get_modifiers(self):
        return TERRAIN_MODIFIERS[self.terrain]

class Board:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for y in range(height)] for x in range(width)]
        self.tile_size = 30  # pixels per tile for pygame rendering

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_area_tiles(self, center_x, center_y, size=2):
        """Get tiles in a 2x2 area centered on given position"""
        tiles = []
        for dx in range(-size//2, size//2 + 1):
            for dy in range(-size//2, size//2 + 1):
                x, y = center_x + dx, center_y + dy
                if self.is_valid_position(x, y):
                    tiles.append(self.get_tile(x, y))
        return tiles

    def render(self, screen):
        """Render the board using pygame"""
        for x in range(self.width):
            for y in range(self.height):
                tile = self.grid[x][y]
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                 self.tile_size, self.tile_size)
                color = TERRAIN_COLORS[tile.terrain]
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Border

    def display(self):
        # Simple text display for debugging
        terrain_symbols = {
            TerrainType.FLAT: '.',
            TerrainType.HIGH_GROUND: '^',
            TerrainType.LOW_GROUND: 'v',
            TerrainType.TRENCHES: '#',
        }
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                row += terrain_symbols[self.grid[x][y].terrain]
            print(row)
