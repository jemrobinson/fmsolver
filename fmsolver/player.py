class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __str__(self):
        return f"{self.name} ({self.score})"

    def __repr__(self):
        return f"({id(self)}: {self.__str__()})"
