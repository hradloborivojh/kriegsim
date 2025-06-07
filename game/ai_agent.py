# ai_agent.py
# Neural network AI agent for kriegsim

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
from typing import List, Tuple, Dict, Any
from collections import deque
from .units import UnitType, Unit
from .board import Board, TerrainType

class WarGameNet(nn.Module):
    """Neural network for tactical war game decision making"""
    
    def __init__(self, input_size=1600, hidden_size=512, output_size=2125):
        super(WarGameNet, self).__init__()
        
        # Input: flattened 20x20x4 board state (1600 dimensions)
        # Output: actions for up to 5 units (25 move + 400 attack each = 425 * 5 = 2125)
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc4 = nn.Linear(hidden_size // 2, output_size)
        
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class GameState:
    """Encodes game state for neural network processing"""
    
    def __init__(self, board: Board, units: List[Unit], current_player: int):
        self.board = board
        self.units = units
        self.current_player = current_player
    
    def to_tensor(self) -> torch.Tensor:
        """Convert game state to neural network input tensor"""
        # Create a multi-channel representation of the board
        # Channels: terrain, player 0 units, player 1 units, hp levels
        
        state = np.zeros((4, self.board.height, self.board.width))
        
        # Channel 0: Terrain encoding
        terrain_encoding = {
            TerrainType.FLAT: 0.25,
            TerrainType.HIGH_GROUND: 0.5,
            TerrainType.LOW_GROUND: 0.0,
            TerrainType.TRENCHES: 0.75
        }
        
        for x in range(self.board.width):
            for y in range(self.board.height):
                tile = self.board.get_tile(x, y)
                state[0, y, x] = terrain_encoding[tile.terrain]
        
        # Channels 1-2: Unit positions and types
        unit_encoding = {
            UnitType.SOLDIER_SQUAD: 0.33,
            UnitType.TANK: 0.66,
            UnitType.MORTAR_SQUAD: 1.0
        }
        
        for unit in self.units:
            if unit.hp > 0:
                channel = 1 if unit.owner == 0 else 2
                state[channel, unit.y, unit.x] = unit_encoding[unit.unit_type]
        
        # Channel 3: HP levels (normalized)
        for unit in self.units:
            if unit.hp > 0:
                state[3, unit.y, unit.x] = unit.hp / unit.max_hp()
        
        return torch.FloatTensor(state.flatten())

class AIAgent:
    """AI Agent using neural network for decision making"""
    
    def __init__(self, player_id: int, learning_rate=0.001):
        self.player_id = player_id
        self.network = WarGameNet()
        self.target_network = WarGameNet()
        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=learning_rate)
        self.memory = deque(maxlen=10000)
        self.epsilon = 0.9  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.95  # Discount factor
        
        # Copy weights to target network
        self.update_target_network()
    
    def update_target_network(self):
        """Copy main network weights to target network"""
        self.target_network.load_state_dict(self.network.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def choose_action(self, game_state: GameState, valid_actions: List[int]) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return random.choice(valid_actions)
        
        state_tensor = game_state.to_tensor().unsqueeze(0)
        q_values = self.network(state_tensor)
        
        # Mask invalid actions
        masked_q_values = q_values.clone()
        mask = torch.ones_like(q_values) * float('-inf')
        mask[0, valid_actions] = 0
        masked_q_values += mask
        
        return masked_q_values.argmax().item()
    
    def replay(self, batch_size=32):
        """Train the network on a batch of experiences"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([e[0] for e in batch])
        actions = torch.LongTensor([e[1] for e in batch])
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.BoolTensor([e[4] for e in batch])
        
        current_q_values = self.network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def get_valid_actions(self, game_state: GameState) -> List[int]:
        """Get list of valid action indices for current game state"""
        valid_actions = []
        my_units = [u for u in game_state.units if u.owner == self.player_id and u.hp > 0]
        
        action_id = 0
        
        # Simplified action space: for each unit, try moving to nearby positions
        for unit_idx, unit in enumerate(my_units):
            if not unit.has_moved and not unit.has_attacked:
                # Movement actions (nearby positions only)
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx == 0 and dy == 0:
                            continue
                        new_x, new_y = unit.x + dx, unit.y + dy
                        if unit.can_move_to(new_x, new_y, game_state.board):
                            valid_actions.append(action_id)
                        action_id += 1
                
                # Attack actions (in range targets)
                for x in range(game_state.board.width):
                    for y in range(game_state.board.height):
                        distance = abs(unit.x - x) + abs(unit.y - y)
                        current_tile = game_state.board.get_tile(unit.x, unit.y)
                        attack_range = unit.attack_range(current_tile.terrain)
                        
                        if distance <= attack_range:
                            target_tile = game_state.board.get_tile(x, y)
                            if (target_tile and target_tile.occupant and 
                                target_tile.occupant.owner != self.player_id):
                                valid_actions.append(action_id)
                        action_id += 1
            else:
                # Skip actions for units that already moved/attacked
                action_id += 25 + (game_state.board.width * game_state.board.height)
        
        return valid_actions if valid_actions else [0]  # Always have at least one action
    
    def decode_action(self, action: int, game_state: GameState) -> Dict[str, Any]:
        """Decode action index into game action"""
        my_units = [u for u in game_state.units if u.owner == self.player_id and u.hp > 0]
        
        if not my_units:
            return {'type': 'noop'}
        
        # Find which unit and action type
        actions_per_unit = 25 + (game_state.board.width * game_state.board.height)
        unit_idx = action // actions_per_unit
        
        if unit_idx >= len(my_units):
            return {'type': 'noop'}
        
        unit = my_units[unit_idx]
        local_action = action % actions_per_unit
        
        if local_action < 25:  # Movement action (5x5 grid around unit, excluding center)
            move_actions = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx != 0 or dy != 0:
                        move_actions.append((dx, dy))
            
            if local_action < len(move_actions):
                dx, dy = move_actions[local_action]
                target_x, target_y = unit.x + dx, unit.y + dy
                return {'type': 'move', 'unit': unit, 'target': (target_x, target_y)}
        else:  # Attack action
            attack_action = local_action - 25
            target_x = attack_action % game_state.board.width
            target_y = attack_action // game_state.board.width
            return {'type': 'attack', 'unit': unit, 'target': (target_x, target_y)}
        
        return {'type': 'noop'}

def calculate_reward(game_state: GameState, action: Dict[str, Any], player_id: int) -> float:
    """Calculate reward for a given action"""
    reward = 0.0
    
    if action['type'] == 'attack':
        # High reward for successful attacks
        target_pos = action['target']
        target_tile = game_state.board.get_tile(target_pos[0], target_pos[1])
        if target_tile and target_tile.occupant:
            enemy_unit = target_tile.occupant
            if enemy_unit.owner != player_id:
                damage = action['unit'].calculate_damage(enemy_unit, target_tile.terrain)
                reward += damage * 20  # Higher reward for damage
                
                if damage >= enemy_unit.hp:
                    reward += 100  # Big bonus for destroying enemy unit
    
    elif action['type'] == 'move':
        # Small reward for positioning
        reward += 2.0
        
        # Bonus for moving toward enemies
        target_pos = action['target']
        unit_pos = (action['unit'].x, action['unit'].y)
        
        # Find closest enemy
        min_enemy_dist = float('inf')
        for unit in game_state.units:
            if unit.owner != player_id and unit.hp > 0:
                enemy_dist = abs(target_pos[0] - unit.x) + abs(target_pos[1] - unit.y)
                min_enemy_dist = min(min_enemy_dist, enemy_dist)
        
        # Reward for getting closer to enemies
        if min_enemy_dist < float('inf'):
            old_dist = abs(unit_pos[0] - target_pos[0]) + abs(unit_pos[1] - target_pos[1])
            if min_enemy_dist < 5:  # Close to enemy
                reward += 10.0
        
        # Bonus for strategic positions
        target_tile = game_state.board.get_tile(target_pos[0], target_pos[1])
        if target_tile.terrain == TerrainType.HIGH_GROUND:
            reward += 8.0
        elif target_tile.terrain == TerrainType.TRENCHES:
            reward += 5.0
    
    return reward
