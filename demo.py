# demo.py
# Quick demo script for kriegsim

from game.game_manager import GameManager
import time

def quick_demo():
    """Run a quick visual demo of the game"""
    print("Kriegsim - Tactical War Game Demo")
    print("=" * 40)
    print("Features demonstrated:")
    print("• 20x20 battlefield with 4 terrain types")
    print("• 3 unit types with unique abilities")
    print("• Neural network AI agents")
    print("• Real-time combat simulation")
    print("• Terrain-based tactical bonuses")
    print()
    
    game = GameManager(1000, 700)
    
    print("Starting demo game...")
    print("Close the window when you're done watching!")
    
    try:
        game.run_visual_game()
    except Exception as e:
        print(f"Demo error: {e}")
    finally:
        game.quit()

if __name__ == "__main__":
    quick_demo()
