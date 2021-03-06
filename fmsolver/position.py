class Position:
    def __init__(self, idx: int, name: str):
        self.number = idx
        self.name = name
        self.players = []

    @property
    def n_players(self):
        return len(self.players)

    @property
    def max_score(self):
        return max([p.score for p in self.players])

    def player(self, idx):
        return self.players[idx]

    def __str__(self):
        return f"Position {self.name} :: {self.n_players} players"

    def __repr__(self):
        return f"({id(self)}: {self.__str__()})"
