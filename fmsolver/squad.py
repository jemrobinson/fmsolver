import functools
import itertools
import tqdm
import yaml
from .player import Player
from .position import Position
from .team import Team

class Squad():
    penalty = 9999

    def __init__(self, filename, exclude=[], min_score=0.0):
        with open(filename) as f_input:
            raw_data = yaml.safe_load(f_input)

        self.positions = [Position(idx, name) for idx, name in enumerate(raw_data.keys())]
        self.teams = [None, None, None]

        for position in self.positions:
            for entry in raw_data[position.name]:
                name, score = list(entry.keys())[0], list(entry.values())[0]
                if name in exclude:
                    continue
                if score >= min_score:
                    position.players.append(Player(name, score))
            position.players.append(Player(f"[No {position.name}]", 0.0))

    def summarise_team(self, team):
        total_score, max_score = 0, 0
        for player, position in zip(self.teams[team].players, self.positions):
            print(f"... {position.name:<3} {player.name:<15} {player.score:.1f}")
            total_score += player.score
            max_score += position.max_score
        print(f"Score {total_score} / {max_score}")

    def construct_allowlists(self, min_score, depth, excluded_names):
        allowed = []
        for position in self.positions:
            allowed_in_position = []
            for player in position.players:
                if len(allowed_in_position) >= depth:
                    continue
                if player.score < min_score:
                    continue
                if player.name in excluded_names:
                    continue
                allowed_in_position.append(player)
            allowed.append(allowed_in_position)
        n_permutations = functools.reduce(lambda x, y: x * y, [len(a) for a in allowed])
        return (allowed, n_permutations)

    def __pick_team(self, permutations):
        best_score, best_team = self.penalty, None
        max_scores = [position.max_score for position in self.positions]
        for permutation in permutations:
            team = Team(permutation)
            if team.is_valid():
                team_score = team.loss_function(max_scores)
                if team_score < best_score:
                    best_score = team_score
                    best_team = team
                    if best_score == 0:
                        break
        return best_team

    def pick_first_team(self, min_score=0.5, depth=99):
        (allowed, n_permutations) = self.construct_allowlists(min_score, depth, [])
        permutations = tqdm.tqdm(itertools.product(*allowed), total=n_permutations, desc="Picking first team")
        self.teams[0] = self.__pick_team(permutations)
        if self.teams[0]:
            self.teams[0].summarise(self.positions)

    def pick_second_team(self, min_score=0.0, depth=99):
        if self.teams[0]:
            (allowed, n_permutations) = self.construct_allowlists(min_score, depth, self.teams[0].names)
            permutations = tqdm.tqdm(itertools.product(*allowed), total=n_permutations, desc="Picking second team")
            self.teams[1] = self.__pick_team(permutations)
        if self.teams[1]:
            self.teams[1].summarise(self.positions)

    def pick_third_team(self, min_score=0.0, depth=99):
        if self.teams[0] and self.teams[1]:
            excluded_names = self.teams[0].names + self.teams[1].names
            (allowed, n_permutations) = self.construct_allowlists(min_score, depth, excluded_names)
            permutations = tqdm.tqdm(itertools.product(*allowed), total=n_permutations, desc="Picking third team")
            self.teams[2] = self.__pick_team(permutations)
        if self.teams[2]:
            self.teams[2].summarise(self.positions)

    def list_others(self, min_score=0.0, depth=99):
        remaining_names = set()
        excluded_names = sum([self.teams[idx].names for idx in range(3) if self.teams[idx]], [])
        for position in self.positions:
            for player in position.players:
                if player.name not in excluded_names and player.score > 0.0:
                    remaining_names.add(player.name)
        print("Remaining players:")
        for name in sorted(remaining_names):
            print(f"... {name}")
