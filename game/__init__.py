# __init__.py
# Initialize the kriegsim game package

from .board import Board, TerrainType
from .units import Unit, UnitType, create_unit
from .turn_manager import TurnManager
from .ai_agent import AIAgent, GameState
from .game_manager import GameManager

__all__ = [
    'Board', 'TerrainType',
    'Unit', 'UnitType', 'create_unit',
    'TurnManager',
    'AIAgent', 'GameState',
    'GameManager'
]
