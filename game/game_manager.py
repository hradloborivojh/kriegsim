# game_manager.py
# Main game manager for kriegsim tactical war game

import pygame
import random
import time
from typing import List, Dict, Optional, Tuple
from .board import Board, TerrainType
from .units import Unit, UnitType, create_unit
from .ai_agent import AIAgent, GameState, calculate_reward
from .turn_manager import TurnManager

class GameManager:
    """Main game manager handling game loop, AI agents, and learning"""
    
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Kriegsim - Tactical War Game")
        self.clock = pygame.time.Clock()
        
        # Game components
        self.board = Board(20, 20)
        self.units = []
        self.turn_manager = TurnManager([0, 1])  # Two players
        
        # AI agents
        self.agents = {
            0: AIAgent(0),
            1: AIAgent(1)
        }
        
        # Game state
        self.running = True
        self.game_over = False
        self.winner = None
        self.turn_count = 0
        self.max_turns = 200
        
        # Learning statistics
        self.game_count = 0
        self.wins = {0: 0, 1: 0}
        
        # UI
        self.font = pygame.font.Font(None, 24)
        
        self.setup_initial_units()
    
    def setup_initial_units(self):
        """Setup initial unit positions for both players"""
        self.units.clear()
        
        # Player 0 units (left side)
        player0_units = [
            (UnitType.SOLDIER_SQUAD, 1, 5),
            (UnitType.SOLDIER_SQUAD, 2, 6),
            (UnitType.SOLDIER_SQUAD, 1, 7),
            (UnitType.TANK, 0, 6),
            (UnitType.MORTAR_SQUAD, 0, 10),
        ]
        
        # Player 1 units (right side)
        player1_units = [
            (UnitType.SOLDIER_SQUAD, 18, 5),
            (UnitType.SOLDIER_SQUAD, 17, 6),
            (UnitType.SOLDIER_SQUAD, 18, 7),
            (UnitType.TANK, 19, 6),
            (UnitType.MORTAR_SQUAD, 19, 10),
        ]
        
        # Create units for player 0
        for unit_type, x, y in player0_units:
            unit = create_unit(unit_type, 0, x, y)
            unit.id = len(self.units)
            self.units.append(unit)
            tile = self.board.get_tile(x, y)
            if tile:
                tile.occupant = unit
        
        # Create units for player 1
        for unit_type, x, y in player1_units:
            unit = create_unit(unit_type, 1, x, y)
            unit.id = len(self.units)
            self.units.append(unit)
            tile = self.board.get_tile(x, y)
            if tile:
                tile.occupant = unit
    
    def get_game_state(self) -> GameState:
        """Get current game state for AI processing"""
        return GameState(self.board, self.units, self.turn_manager.get_current_player())
    
    def check_victory_conditions(self) -> Optional[int]:
        """Check if game has ended and return winner"""
        alive_units = {0: [], 1: []}
        
        for unit in self.units:
            if unit.hp > 0:
                alive_units[unit.owner].append(unit)
        
        # Check elimination victory
        if len(alive_units[0]) == 0:
            return 1
        elif len(alive_units[1]) == 0:
            return 0
        
        # Check turn limit
        if self.turn_count >= self.max_turns:
            # Winner is player with more units
            if len(alive_units[0]) > len(alive_units[1]):
                return 0
            elif len(alive_units[1]) > len(alive_units[0]):
                return 1
            else:
                return None  # Draw
        
        return None
    
    def execute_action(self, action: Dict[str, any]) -> float:
        """Execute an action and return reward"""
        current_player = self.turn_manager.get_current_player()
        reward = 0.0
        
        if action['type'] == 'move':
            unit = action['unit']
            target = action['target']
            
            if unit.can_move_to(target[0], target[1], self.board):
                unit.move_to(target[0], target[1], self.board)
                reward = calculate_reward(self.get_game_state(), action, current_player)
        
        elif action['type'] == 'attack':
            unit = action['unit']
            target = action['target']
            
            # Check if attack is valid
            distance = abs(unit.x - target[0]) + abs(unit.y - target[1])
            current_tile = self.board.get_tile(unit.x, unit.y)
            attack_range = unit.attack_range(current_tile.terrain)
            
            if distance <= attack_range and not unit.has_attacked:
                damage_results = unit.attack_target(target[0], target[1], self.board)
                
                # Apply damage
                for x, y, damage in damage_results:
                    target_tile = self.board.get_tile(x, y)
                    if target_tile and target_tile.occupant:
                        target_unit = target_tile.occupant
                        target_unit.hp = max(0, target_unit.hp - damage)
                        
                        # Remove destroyed units
                        if target_unit.hp <= 0:
                            target_tile.occupant = None
                
                reward = calculate_reward(self.get_game_state(), action, current_player)
        
        return reward
    
    def ai_turn(self):
        """Execute one AI turn"""
        current_player = self.turn_manager.get_current_player()
        agent = self.agents[current_player]
        
        # Get current game state
        game_state = self.get_game_state()
        state_tensor = game_state.to_tensor()
        
        # Get valid actions
        valid_actions = agent.get_valid_actions(game_state)
        
        if not valid_actions:
            return {'type': 'noop'}
        
        # Choose action
        action_idx = agent.choose_action(game_state, valid_actions)
        action = agent.decode_action(action_idx, game_state)
        
        # Execute action and get reward
        reward = self.execute_action(action)
        
        # Store experience for learning
        next_game_state = self.get_game_state()
        next_state_tensor = next_game_state.to_tensor()
        done = self.check_victory_conditions() is not None
        
        agent.remember(state_tensor.numpy(), action_idx, reward, 
                      next_state_tensor.numpy(), done)
        
        # Train the agent periodically
        if len(agent.memory) > 100 and self.turn_count % 5 == 0:
            agent.replay()
        
        return action
    
    def reset_units_turn_state(self):
        """Reset all units' turn state"""
        for unit in self.units:
            if unit.hp > 0:
                unit.reset_turn()
    
    def next_turn(self):
        """Advance to next turn"""
        self.reset_units_turn_state()
        self.turn_manager.next_turn()
        
        if self.turn_manager.get_current_player() == 0:
            self.turn_count += 1
    
    def run_ai_game(self, max_games=1000):
        """Run multiple AI vs AI games for learning"""
        print(f"Starting training with {max_games} games...")
        
        for game_num in range(max_games):
            if game_num % 5 == 0:
                print(f"Starting game {game_num}...")
            
            self.reset_game()
            turn_limit = 0
            
            while not self.game_over and turn_limit < 100:  # Shorter limit for testing
                # AI turn
                try:
                    action = self.ai_turn()
                    if turn_limit % 20 == 0 and game_num < 3:
                        print(f"  Turn {turn_limit}, Action: {action['type']}")
                except Exception as e:
                    print(f"Error in AI turn: {e}")
                    break
                
                # Check victory
                winner = self.check_victory_conditions()
                if winner is not None:
                    self.game_over = True
                    self.winner = winner
                    self.wins[winner] += 1
                    if game_num < 3:
                        print(f"  Game {game_num} ended: Player {winner} wins after {turn_limit} turns")
                    break
                else:
                    self.next_turn()
                    turn_limit += 1
            
            if turn_limit >= 100:
                # Game too long, call it a draw
                self.game_over = True
                if game_num < 3:
                    print(f"  Game {game_num} ended: Turn limit reached")
            
            self.game_count += 1
            
            # Print progress
            if game_num % 5 == 0 and game_num > 0:
                win_rate_0 = self.wins[0] / max(1, self.game_count)
                win_rate_1 = self.wins[1] / max(1, self.game_count)
                avg_epsilon = (self.agents[0].epsilon + self.agents[1].epsilon) / 2
                print(f"Game {game_num}: P0: {win_rate_0:.1%}, P1: {win_rate_1:.1%}, ε: {avg_epsilon:.3f}")
        
        print("Training completed!")
    
    def run_visual_game(self):
        """Run game with visual interface"""
        turn_limit = 0
        while self.running:
            self.handle_events()
            
            if not self.game_over and turn_limit < 500:
                # AI turn
                action = self.ai_turn()
                
                # Check victory
                winner = self.check_victory_conditions()
                if winner is not None:
                    self.game_over = True
                    self.winner = winner
                    print(f"Game Over! Player {winner} wins!")
                else:
                    self.next_turn()
                    turn_limit += 1
                
                # Add small delay for visualization
                time.sleep(0.1)
            elif turn_limit >= 500:
                self.game_over = True
                print("Game ended due to turn limit!")
            
            self.render()
            self.clock.tick(10)  # 10 FPS for visibility
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
    
    def render(self):
        """Render the game state"""
        self.screen.fill((50, 50, 50))
        
        # Render board
        self.board.render(self.screen)
        
        # Render units
        for unit in self.units:
            if unit.hp > 0:
                unit.render(self.screen, self.board)
        
        # Render UI
        self.render_ui()
        
        pygame.display.flip()
    
    def render_ui(self):
        """Render game UI information"""
        # Turn info
        current_player = self.turn_manager.get_current_player()
        turn_text = self.font.render(f"Turn: {self.turn_count} | Player: {current_player}", 
                                   True, (255, 255, 255))
        self.screen.blit(turn_text, (10, 10))
        
        # Unit counts
        alive_units = {0: 0, 1: 0}
        for unit in self.units:
            if unit.hp > 0:
                alive_units[unit.owner] += 1
        
        units_text = self.font.render(f"P0 Units: {alive_units[0]} | P1 Units: {alive_units[1]}", 
                                    True, (255, 255, 255))
        self.screen.blit(units_text, (10, 35))
        
        # Game over message
        if self.game_over:
            if self.winner is not None:
                winner_text = self.font.render(f"Player {self.winner} Wins! Press R to restart", 
                                             True, (255, 255, 0))
            else:
                winner_text = self.font.render("Draw! Press R to restart", True, (255, 255, 0))
            
            text_rect = winner_text.get_rect(center=(self.screen.get_width()//2, 100))
            self.screen.blit(winner_text, text_rect)
    
    def reset_game(self):
        """Reset game to initial state"""
        self.game_over = False
        self.winner = None
        self.turn_count = 0
        self.turn_manager = TurnManager([0, 1])
        self.board = Board(20, 20)
        self.setup_initial_units()
    
    def quit(self):
        """Clean up and quit"""
        pygame.quit()
