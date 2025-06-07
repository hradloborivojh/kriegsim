#!/usr/bin/env python3
# main.py
# Main entry point for kriegsim tactical war game

import sys
import argparse
from game.game_manager import GameManager

def main():
    parser = argparse.ArgumentParser(description='Kriegsim - Tactical War Game with Neural Network AI')
    parser.add_argument('--mode', choices=['visual', 'training'], default='visual',
                       help='Game mode: visual (with pygame display) or training (AI learning)')
    parser.add_argument('--games', type=int, default=1000,
                       help='Number of games to run in training mode')
    parser.add_argument('--width', type=int, default=800,
                       help='Window width for visual mode')
    parser.add_argument('--height', type=int, default=600,
                       help='Window height for visual mode')
    
    args = parser.parse_args()
    
    # Create game manager
    game_manager = GameManager(args.width, args.height)
    
    try:
        if args.mode == 'visual':
            print("Starting visual game mode...")
            print("Watch AI agents battle it out!")
            print("Press R to restart when game ends, or close window to quit.")
            game_manager.run_visual_game()
        
        elif args.mode == 'training':
            print(f"Starting AI training mode for {args.games} games...")
            print("Neural networks will learn to play the game through self-play.")
            game_manager.run_ai_game(args.games)
            print("Training completed!")
            
            # Print final statistics
            total_games = game_manager.game_count
            if total_games > 0:
                win_rate_0 = game_manager.wins[0] / total_games
                win_rate_1 = game_manager.wins[1] / total_games
                print(f"\nFinal Results after {total_games} games:")
                print(f"Player 0 win rate: {win_rate_0:.2%}")
                print(f"Player 1 win rate: {win_rate_1:.2%}")
                print(f"Draws: {(total_games - game_manager.wins[0] - game_manager.wins[1]) / total_games:.2%}")
    
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    
    finally:
        game_manager.quit()

if __name__ == "__main__":
    main()
