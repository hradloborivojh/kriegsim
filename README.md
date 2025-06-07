# Kriegsim - Neural Network Tactical War Game

A sophisticated turn-based tactical war simulation game featuring neural network AI agents that learn through self-play.

## Features

### 🎮 Game Mechanics
- **20x20 Battlefield**: Large tactical grid with varied terrain
- **4 Terrain Types**: Flat, High Ground, Low Ground, and Trenches
- **Strategic Combat**: Terrain affects movement, defense, and attack range
- **Turn-Based Strategy**: Classic tactical gameplay with modern AI

### 🤖 Unit Types
- **Soldier Squad (1/1)**: Range 2, Speed 1, instant attack
- **Tank (1/5)**: Range 5, Speed 1, 2x2 AoE attack, instant
- **Mortar Squad (5/1)**: Range 10, Speed 1, 2x2 AoE, 1-turn delay

### 🧠 AI Learning System
- **Neural Network Agents**: Deep learning AI that improves through gameplay
- **Self-Play Training**: AI agents learn by playing against each other
- **Experience Replay**: Advanced learning techniques for strategy development
- **Dynamic Strategy**: AI adapts tactics based on terrain and unit positioning

### 🎯 Tactical Elements
- **High Ground Advantage**: +1 attack range, defensive penalties for targets below
- **Trench Warfare**: Soldiers get enhanced defense (1/2 instead of 1/1)
- **Area of Effect**: Tanks and mortars can hit multiple targets
- **Delayed Attacks**: Mortar squads have realistic artillery timing

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd kriegsim

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Visual Mode (Watch AI Battle)
```bash
python main.py --mode visual
```
Watch neural network agents battle in real-time with pygame visualization.

### Training Mode (AI Learning)
```bash
python main.py --mode training --games 5000
```
Train AI agents through thousands of self-play games.

### Quick Demo
```bash
python demo.py
```
Run a quick demonstration of the game features.

## Game Controls

- **Visual Mode**: Watch the AI play automatically
- **R Key**: Restart game when it ends
- **Close Window**: Exit the game

## Technical Architecture

### Neural Network
- **Input**: 800-dimensional game state (flattened 20x20x4 board representation)
- **Architecture**: 4-layer fully connected network with dropout
- **Output**: 400 possible actions (movement and attack combinations)
- **Learning**: Deep Q-Learning with experience replay

### Game State Encoding
- **Channel 0**: Terrain types (normalized values)
- **Channel 1**: Player 0 units and types
- **Channel 2**: Player 1 units and types  
- **Channel 3**: Unit health levels

### AI Features
- **Epsilon-Greedy Exploration**: Balances exploration vs exploitation
- **Target Network**: Stable learning with periodic weight updates
- **Experience Replay**: Learn from past experiences
- **Reward System**: Tactical bonuses for smart positioning and combat

## Development

The game uses object-oriented design with clear separation of concerns:

- `board.py`: Terrain system and battlefield management
- `units.py`: Unit types, combat mechanics, and movement
- `ai_agent.py`: Neural network AI implementation
- `game_manager.py`: Main game loop and coordination
- `turn_manager.py`: Turn-based game flow

## Future Enhancements

- [ ] More unit types and abilities
- [ ] Multiplayer human vs AI mode
- [ ] Campaign mode with progressive difficulty
- [ ] Advanced AI architectures (CNN, attention mechanisms)
- [ ] Replay system for analyzing AI strategies
- [ ] Tournament mode between different AI models

## License

MIT License - Feel free to use and modify for your own projects!