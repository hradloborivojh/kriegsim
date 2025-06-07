#!/usr/bin/env python3
"""
Visual demo of kriegsim - shows the game window with AI vs AI combat
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_manager import GameManager

def main():
    print("🎮 Starting Kriegsim Visual Demo...")
    print("Opening pygame window with:")
    print("  ✓ 20x20 battlefield with colored terrain")
    print("  ✓ Units as colored circles (green=soldiers, gray=tanks, brown=mortars)")
    print("  ✓ AI players battling automatically")
    print("  ✓ Real-time combat visualization")
    print()
    print("Controls:")
    print("  - Close window to exit")
    print("  - Press R when game ends to restart")
    print("  - Watch the AI battle it out!")
    print()
    
    # Create game with larger window for better visibility
    game = GameManager(width=1200, height=800)
    
    try:
        print("🚀 Launching game window...")
        game.run_visual_game()
    except KeyboardInterrupt:
        print("\n❌ Game interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        game.quit()
        print("✅ Game window closed")

if __name__ == "__main__":
    main()
