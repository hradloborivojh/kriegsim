#!/usr/bin/env python3
# test_game.py
# Test script to verify all game components work

import sys
from game.board import Board, TerrainType
from game.units import Unit, UnitType, create_unit
from game.ai_agent import AIAgent, GameState
from game.game_manager import GameManager

def test_basic_components():
    """Test basic game components"""
    print("Testing game components...")
    
    # Test board
    board = Board(10, 10)
    print(f"✓ Board created: {board.width}x{board.height}")
    
    # Test units
    unit = create_unit(UnitType.SOLDIER_SQUAD, 0, 5, 5)
    board.get_tile(5, 5).occupant = unit
    print(f"✓ Unit created: {unit.unit_type} at ({unit.x}, {unit.y})")
    
    # Test AI agent
    agent = AIAgent(0)
    print(f"✓ AI agent created with epsilon: {agent.epsilon}")
    
    # Test game state
    units = [unit]
    game_state = GameState(board, units, 0)
    state_tensor = game_state.to_tensor()
    print(f"✓ Game state tensor shape: {state_tensor.shape}")
    
    # Test valid actions
    valid_actions = agent.get_valid_actions(game_state)
    print(f"✓ Valid actions found: {len(valid_actions)}")
    
    if valid_actions:
        action_idx = valid_actions[0]
        action = agent.decode_action(action_idx, game_state)
        print(f"✓ Action decoded: {action['type']}")
    
    print("\n✅ All basic tests passed!")
    return True

def test_game_manager():
    """Test game manager without GUI"""
    print("\nTesting game manager...")
    
    try:
        # Create game manager (this initializes pygame)
        game = GameManager()
        print("✓ Game manager created")
        
        # Test unit setup
        print(f"✓ Units created: {len(game.units)}")
        
        # Test one AI turn
        try:
            action = game.ai_turn()
            print(f"✓ AI turn executed: {action['type']}")
        except Exception as e:
            print(f"✗ AI turn failed: {e}")
            return False
        
        # Clean up
        game.quit()
        print("✓ Game manager cleaned up")
        
        print("\n✅ Game manager tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Game manager test failed: {e}")
        return False

def main():
    print("Kriegsim Component Test Suite")
    print("=" * 40)
    
    success = True
    
    try:
        success &= test_basic_components()
        success &= test_game_manager()
        
        if success:
            print("\n🎉 All tests passed! The game is ready to run.")
            print("\nTry these commands:")
            print("  python main.py --mode visual    # Watch AI battle")
            print("  python main.py --mode training  # Train AI agents")
            print("  python demo.py                  # Quick demo")
        else:
            print("\n❌ Some tests failed. Check the errors above.")
            
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        success = False
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
