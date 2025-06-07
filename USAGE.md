# Kriegsim Usage Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run visual demo:**
   ```bash
   python demo.py
   ```

3. **Watch AI battle (visual mode):**
   ```bash
   python main.py --mode visual
   ```

4. **Train AI agents:**
   ```bash
   python main.py --mode training --games 1000
   ```

## Game Features in Action

### Neural Network Learning
- **Epsilon Decay**: Watch ε decrease as AI becomes more confident
- **Self-Play**: AI improves by playing against itself
- **Strategic Evolution**: Early games show random movement, later games show tactical positioning

### Tactical Combat
- **Terrain Advantage**: Units automatically gain bonuses on high ground and trenches
- **Area Attacks**: Tanks and mortars hit multiple targets
- **Range Warfare**: Different units have different attack ranges

### Unit Types
- **🟢 Soldier Squad**: Fast, versatile infantry
- **⚪ Tank**: Heavy armor with area attacks  
- **🟤 Mortar Squad**: Long-range artillery with delayed fire

### Terrain Types
- **🟢 Flat**: No bonuses
- **🟤 High Ground**: +1 attack range
- **🔵 Low Ground**: -1 defense
- **⚫ Trenches**: +1 defense for soldiers

## Advanced Usage

### Training Parameters
```bash
# Long training session
python main.py --mode training --games 5000

# Custom window size for visual mode
python main.py --mode visual --width 1200 --height 800
```

### Monitoring Learning
The training output shows:
- **Win rates**: Which AI is performing better
- **Epsilon values**: How much the AI is exploring vs exploiting
- **Game duration**: How quickly games resolve

### Expected Learning Progression
1. **Games 1-100**: Random movement, mostly draws
2. **Games 100-500**: Basic positioning, some combat
3. **Games 500+**: Advanced tactics, terrain usage, coordinated attacks

## Tips for Observation

### What to Watch For
- **Early Training**: Units move randomly, avoid combat
- **Mid Training**: Units start grouping, positioning on terrain
- **Late Training**: Coordinated attacks, strategic retreats

### Visual Indicators
- **Health Bars**: Green→Yellow→Red showing unit damage
- **Unit Colors**: Player 0 (darker) vs Player 1 (lighter)
- **Terrain Colors**: Each type has distinct coloring

## Technical Details

### Performance
- Training: ~10-50 games per second
- Visual: 10 FPS for easy viewing
- Memory: Moderate PyTorch usage

### Learning Algorithm
- **Deep Q-Learning**: Value-based reinforcement learning
- **Experience Replay**: Learn from past games
- **Target Networks**: Stable training targets

Enjoy watching AI learn to wage tactical warfare! 🎮
