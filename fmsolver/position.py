from collections import OrderedDict

class Position():
    def __init__(self, idx, name):
        self.number = idx
        self.name = name
        self.players = OrderedDict()

    @property
    def n_players(self):
        return len(self.players)

    @property
    def max_score(self):
        return max(self.players.values())

    def player(self, idx):
        return list(self.players.items())[idx]

    def __str__(self):
        return f"Position {self.name}"
