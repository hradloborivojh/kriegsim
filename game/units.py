# units.py
# Defines unit types, attributes, and logic for kriegsim tactical war game

from enum import Enum, auto
from typing import Optional, Dict, Any, List, Tuple
import pygame
from .board import TerrainType

class UnitType(Enum):
    SOLDIER_SQUAD = auto()  # 1/1, Range 2, Speed 1, instant attack
    TANK = auto()           # 1/5, Range 5, Speed 1, 2x2 AoE, instant
    MORTAR_SQUAD = auto()   # 5/1, Range 10, Speed 1, 2x2 AoE, 1-turn delay

# Color coding for units
UNIT_COLORS = {
    UnitType.SOLDIER_SQUAD: (0, 100, 0),    # Dark green
    UnitType.TANK: (128, 128, 128),         # Gray
    UnitType.MORTAR_SQUAD: (139, 69, 19),   # Brown
}

class Unit:
    def __init__(self, unit_type: UnitType, owner: int, x: int = 0, y: int = 0):
        self.unit_type = unit_type
        self.owner = owner  # Player ID (0 or 1)
        self.x = x
        self.y = y
        self.hp = self.max_hp()
        self.has_moved = False
        self.has_attacked = False
        self.id = None  # Will be set by game manager

    def max_hp(self):
        return UNIT_STATS[self.unit_type]['hp']

    def attack_power(self):
        return UNIT_STATS[self.unit_type]['attack']

    def defense_power(self, terrain: Optional[TerrainType] = None):
        base_def = UNIT_STATS[self.unit_type]['defense']
        
        # Special case: soldiers in trenches get enhanced defense
        if (self.unit_type == UnitType.SOLDIER_SQUAD and 
            terrain == TerrainType.TRENCHES):
            return base_def + 1  # Becomes 1/2 instead of 1/1
        
        return base_def

    def movement_speed(self):
        return UNIT_STATS[self.unit_type]['speed']

    def attack_range(self, terrain: Optional[TerrainType] = None):
        base_range = UNIT_STATS[self.unit_type]['range']
        
        # High ground bonus
        if terrain == TerrainType.HIGH_GROUND:
            return base_range + 1
        
        return base_range

    def can_attack_area(self):
        """Returns True if unit has area of effect attacks"""
        return UNIT_STATS[self.unit_type]['aoe']

    def attack_delay(self):
        """Returns number of turns delay for attack (0 = instant)"""
        return UNIT_STATS[self.unit_type]['delay']

    def can_move_to(self, x: int, y: int, board) -> bool:
        """Check if unit can move to given position"""
        if not board.is_valid_position(x, y):
            return False
        
        tile = board.get_tile(x, y)
        if tile.occupant is not None:
            return False
        
        distance = abs(self.x - x) + abs(self.y - y)
        return distance <= self.movement_speed()

    def move_to(self, x: int, y: int, board):
        """Move unit to new position"""
        old_tile = board.get_tile(self.x, self.y)
        new_tile = board.get_tile(x, y)
        
        if old_tile:
            old_tile.occupant = None
        if new_tile:
            new_tile.occupant = self
        
        self.x = x
        self.y = y
        self.has_moved = True

    def attack_target(self, target_x: int, target_y: int, board) -> List[Tuple[int, int, int]]:
        """
        Attack target position. Returns list of (x, y, damage) tuples.
        For delayed attacks, damage is applied later.
        """
        results = []
        
        if self.can_attack_area():
            # Area of effect attack (2x2)
            affected_tiles = board.get_area_tiles(target_x, target_y, 2)
            for tile in affected_tiles:
                if tile and tile.occupant and tile.occupant.owner != self.owner:
                    damage = self.calculate_damage(tile.occupant, tile.terrain)
                    results.append((tile.x, tile.y, damage))
        else:
            # Single target attack
            tile = board.get_tile(target_x, target_y)
            if tile and tile.occupant and tile.occupant.owner != self.owner:
                damage = self.calculate_damage(tile.occupant, tile.terrain)
                results.append((target_x, target_y, damage))
        
        self.has_attacked = True
        return results

    def calculate_damage(self, target: 'Unit', terrain: TerrainType) -> int:
        """Calculate damage dealt to target considering terrain"""
        from .board import TERRAIN_MODIFIERS
        
        attack = self.attack_power()
        defense = target.defense_power(terrain)
        
        # Terrain modifiers
        modifiers = TERRAIN_MODIFIERS.get(terrain, {})
        defense += modifiers.get('defense', 0)
        
        # High ground penalty for targets on low ground
        if terrain == TerrainType.LOW_GROUND:
            defense -= 1
        
        return max(0, attack - defense)

    def reset_turn(self):
        """Reset unit state for new turn"""
        self.has_moved = False
        self.has_attacked = False

    def render(self, screen, board):
        """Render unit on pygame screen"""
        rect = pygame.Rect(self.x * board.tile_size + 5, 
                          self.y * board.tile_size + 5,
                          board.tile_size - 10, 
                          board.tile_size - 10)
        
        color = UNIT_COLORS[self.unit_type]
        if self.owner == 1:
            # Slightly different shade for player 2
            color = tuple(min(255, c + 50) for c in color)
        
        pygame.draw.ellipse(screen, color, rect)
        
        # Draw HP indicator
        hp_ratio = self.hp / self.max_hp()
        hp_width = int((board.tile_size - 10) * hp_ratio)
        hp_rect = pygame.Rect(self.x * board.tile_size + 5,
                             self.y * board.tile_size + board.tile_size - 8,
                             hp_width, 3)
        hp_color = (0, 255, 0) if hp_ratio > 0.5 else (255, 255, 0) if hp_ratio > 0.25 else (255, 0, 0)
        pygame.draw.rect(screen, hp_color, hp_rect)

# Unit stats and abilities
def get_default_unit_stats():
    return {
        UnitType.SOLDIER_SQUAD: {
            'hp': 1,
            'attack': 1,
            'defense': 1,
            'speed': 1,
            'range': 2,
            'aoe': False,
            'delay': 0,  # Instant attack
        },
        UnitType.TANK: {
            'hp': 1,
            'attack': 5,
            'defense': 1,
            'speed': 1,
            'range': 5,
            'aoe': True,  # 2x2 area of effect
            'delay': 0,   # Instant attack
        },
        UnitType.MORTAR_SQUAD: {
            'hp': 5,
            'attack': 1,
            'defense': 1,
            'speed': 1,
            'range': 10,
            'aoe': True,  # 2x2 area of effect
            'delay': 1,   # 1-turn delay
        },
    }

UNIT_STATS = get_default_unit_stats()

# Factory for creating units
def create_unit(unit_type: UnitType, owner: int, x: int = 0, y: int = 0) -> Unit:
    return Unit(unit_type, owner, x, y)
