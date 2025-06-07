"""
Turn Manager and Resource System for kriegsim
"""
class ResourceManager:
    def __init__(self, initial_resources):
        self.resources = initial_resources.copy()

    def spend(self, player, amount):
        if self.resources.get(player, 0) >= amount:
            self.resources[player] -= amount
            return True
        return False

    def add(self, player, amount):
        self.resources[player] = self.resources.get(player, 0) + amount

    def get(self, player):
        return self.resources.get(player, 0)

class TurnManager:
    def __init__(self, players):
        self.players = players
        self.current = 0
        self.phase = 'main'
        self.turn_count = 0

    def next_turn(self):
        self.current = (self.current + 1) % len(self.players)
        self.turn_count += 1
        self.phase = 'main'

    def get_current_player(self):
        return self.players[self.current]

    def set_phase(self, phase):
        self.phase = phase

    def get_phase(self):
        return self.phase

class VictoryConditions:
    def __init__(self, board, resource_manager, control_points=None):
        self.board = board
        self.resource_manager = resource_manager
        self.control_points = control_points or []

    def check_elimination(self, player_units):
        # player_units: dict of player -> list of units
        for player, units in player_units.items():
            if not units:
                return f"{player} eliminated!"
        return None

    def check_control_points(self, player_control):
        # player_control: dict of player -> set of control point positions
        for player, points in player_control.items():
            if len(points) >= len(self.control_points):
                return f"{player} controls all points!"
        return None

    def check_resource_depletion(self):
        for player, amount in self.resource_manager.resources.items():
            if amount <= 0:
                return f"{player} depleted resources!"
        return None

    def check_all(self, player_units, player_control):
        return (
            self.check_elimination(player_units)
            or self.check_control_points(player_control)
            or self.check_resource_depletion()
        )
