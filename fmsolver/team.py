from multiprocessing.sharedctypes import Value


class Team():
    def __init__(self, players=[]):
        self.players = players

    @property
    def names(self):
        return [player.name for player in self.players]

    @property
    def scores(self):
        return [player.score for player in self.players]

    def is_valid(self):
        # Check for non-repeating names.
        return len(set(self.names)) == len(self.names)

    def loss_function(self, max_scores):
        return sum([(max_score - score) for score, max_score in zip(self.scores, max_scores)])

    def summarise(self, positions):
        total_score, max_score = 0, 0
        for player, position in zip(self.players, positions):
            print(f"... {position.name:<3} {player.name:<15} {player.score:.1f}")
            total_score += player.score
            max_score += position.max_score
        print(f"Score {total_score:.1f} / {max_score:.1f}")

    def __str__(self):
        return "; ".join([str(p) for p in self.players])