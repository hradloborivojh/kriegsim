#!/usr/bin/env python3
"""
Text-based demo of kriegsim - shows the game in ASCII format for browser environments
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.board import Board, TerrainType
from game.units import Unit, UnitType, create_unit
from game.turn_manager import TurnManager

class TextGameDisplay:
    """Text-based game display for browser environments"""
    
    def __init__(self):
        self.board = Board(15, 15)  # Smaller for text display
        self.units = []
        self.turn_manager = TurnManager([0, 1])
        self.turn_count = 0
        self.setup_units()
    
    def setup_units(self):
        """Setup initial units"""
        self.units.clear()
        
        # Player 0 units (left side) - represented as numbers
        player0_units = [
            (UnitType.SOLDIER_SQUAD, 1, 3),
            (UnitType.SOLDIER_SQUAD, 2, 4),
            (UnitType.TANK, 0, 4),
            (UnitType.MORTAR_SQUAD, 0, 7),
        ]
        
        # Player 1 units (right side) - represented as letters
        player1_units = [
            (UnitType.SOLDIER_SQUAD, 13, 3),
            (UnitType.SOLDIER_SQUAD, 12, 4),
            (UnitType.TANK, 14, 4),
            (UnitType.MORTAR_SQUAD, 14, 7),
        ]
        
        # Create units
        for unit_type, x, y in player0_units:
            unit = create_unit(unit_type, 0, x, y)
            self.units.append(unit)
            tile = self.board.get_tile(x, y)
            if tile:
                tile.occupant = unit
        
        for unit_type, x, y in player1_units:
            unit = create_unit(unit_type, 1, x, y)
            self.units.append(unit)
            tile = self.board.get_tile(x, y)
            if tile:
                tile.occupant = unit
    
    def display_board(self):
        """Display the game board in text format"""
        print("\n" + "="*60)
        print(f"KRIEGSIM - Turn {self.turn_count} - Player {self.turn_manager.get_current_player()}'s turn")
        print("="*60)
        
        # Terrain symbols
        terrain_symbols = {
            TerrainType.FLAT: '.',
            TerrainType.HIGH_GROUND: '^',
            TerrainType.LOW_GROUND: 'v',
            TerrainType.TRENCHES: '#',
        }
        
        # Unit symbols
        unit_symbols = {
            (UnitType.SOLDIER_SQUAD, 0): '1',  # Player 0 soldiers
            (UnitType.TANK, 0): '2',           # Player 0 tanks
            (UnitType.MORTAR_SQUAD, 0): '3',   # Player 0 mortars
            (UnitType.SOLDIER_SQUAD, 1): 'A',  # Player 1 soldiers
            (UnitType.TANK, 1): 'B',           # Player 1 tanks
            (UnitType.MORTAR_SQUAD, 1): 'C',   # Player 1 mortars
        }
        
        # Display column numbers
        print("   ", end="")
        for x in range(self.board.width):
            print(f"{x:2}", end="")
        print()
        
        # Display board
        for y in range(self.board.height):
            print(f"{y:2} ", end="")
            for x in range(self.board.width):
                tile = self.board.get_tile(x, y)
                
                if tile.occupant and tile.occupant.hp > 0:
                    # Show unit
                    symbol = unit_symbols.get((tile.occupant.unit_type, tile.occupant.owner), '?')
                    print(f" {symbol}", end="")
                else:
                    # Show terrain
                    symbol = terrain_symbols[tile.terrain]
                    print(f" {symbol}", end="")
            print()
        
        # Legend
        print("\nLEGEND:")
        print("Terrain: . = Flat  ^ = High Ground  v = Low Ground  # = Trenches")
        print("Player 0: 1 = Soldiers(1/1)  2 = Tank(1/5)  3 = Mortar(5/1)")
        print("Player 1: A = Soldiers(1/1)  B = Tank(1/5)  C = Mortar(5/1)")
        
        # Unit status
        print("\nUNIT STATUS:")
        alive_0 = [u for u in self.units if u.owner == 0 and u.hp > 0]
        alive_1 = [u for u in self.units if u.owner == 1 and u.hp > 0]
        print(f"Player 0: {len(alive_0)} units alive")
        print(f"Player 1: {len(alive_1)} units alive")
    
    def simulate_turn(self):
        """Simulate a simple AI turn"""
        current_player = self.turn_manager.get_current_player()
        my_units = [u for u in self.units if u.owner == current_player and u.hp > 0]
        enemy_units = [u for u in self.units if u.owner != current_player and u.hp > 0]
        
        if not my_units or not enemy_units:
            return False
        
        # Simple AI: move towards enemies and attack if in range
        import random
        unit = random.choice(my_units)
        enemy = random.choice(enemy_units)
        
        # Try to move closer to enemy
        if not unit.has_moved:
            dx = 1 if enemy.x > unit.x else -1 if enemy.x < unit.x else 0
            dy = 1 if enemy.y > unit.y else -1 if enemy.y < unit.y else 0
            
            new_x = unit.x + dx
            new_y = unit.y + dy
            
            if unit.can_move_to(new_x, new_y, self.board):
                unit.move_to(new_x, new_y, self.board)
                print(f"Player {current_player} moved unit from ({unit.x-dx},{unit.y-dy}) to ({unit.x},{unit.y})")
        
        # Try to attack
        if not unit.has_attacked:
            distance = abs(unit.x - enemy.x) + abs(unit.y - enemy.y)
            current_tile = self.board.get_tile(unit.x, unit.y)
            attack_range = unit.attack_range(current_tile.terrain)
            
            if distance <= attack_range:
                damage = unit.calculate_damage(enemy, self.board.get_tile(enemy.x, enemy.y).terrain)
                enemy.hp = max(0, enemy.hp - damage)
                unit.has_attacked = True
                
                print(f"Player {current_player} attacked! Dealt {damage} damage to enemy at ({enemy.x},{enemy.y})")
                
                if enemy.hp <= 0:
                    print(f"Enemy unit destroyed!")
                    tile = self.board.get_tile(enemy.x, enemy.y)
                    tile.occupant = None
        
        # Reset for next turn
        for unit in self.units:
            if unit.hp > 0:
                unit.has_moved = False
                unit.has_attacked = False
        
        self.turn_manager.next_turn()
        if self.turn_manager.get_current_player() == 0:
            self.turn_count += 1
        
        return True
    
    def check_winner(self):
        """Check if game has ended"""
        alive_0 = [u for u in self.units if u.owner == 0 and u.hp > 0]
        alive_1 = [u for u in self.units if u.owner == 1 and u.hp > 0]
        
        if len(alive_0) == 0:
            return 1
        elif len(alive_1) == 0:
            return 0
        elif self.turn_count >= 50:
            return None  # Draw
        
        return -1  # Continue

def main():
    print("🎮 KRIEGSIM - Text-Based Tactical War Game")
    print("=" * 50)
    print("Watch AI agents battle on a tactical battlefield!")
    print("This is a simplified version for browser environments.")
    print()
    
    game = TextGameDisplay()
    
    # Show initial state
    game.display_board()
    input("\nPress Enter to start the battle...")
    
    # Game loop
    while True:
        if not game.simulate_turn():
            break
        
        game.display_board()
        
        winner = game.check_winner()
        if winner == -1:
            time.sleep(1)  # Pause between turns
            continue
        elif winner is None:
            print("\n🤝 DRAW! Maximum turns reached.")
            break
        else:
            print(f"\n🎉 PLAYER {winner} WINS!")
            break
    
    print("\nGame Over! Thanks for watching Kriegsim in action! 🎮")

if __name__ == "__main__":
    main()
