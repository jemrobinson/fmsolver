import functools
import itertools
from math import perm
import tqdm
import yaml
from .player import Player
from .position import Position
from .team import Team


class Squad:
    penalty = 9999

    def __init__(self, filename, exclude=[], n_subs=0, min_score=0.0):
        with open(filename) as f_input:
            raw_data = yaml.safe_load(f_input)

        self.positions = [
            Position(idx, name)
            for idx, name in enumerate(
                [k for k in raw_data.keys() if k != "substitutes"]
            )
        ]
        self.substitutes = []
        self.excluded_names = []
        self.teams = {}

        for position in self.positions:
            for entry in raw_data[position.name]:
                name, score = list(entry.keys())[0], list(entry.values())[0]
                if name in exclude:
                    continue
                if score >= min_score:
                    position.players.append(Player(name, score))
            position.players.append(Player(f"[No {position.name}]", 0.0))

        for idx, position_data in enumerate(raw_data["substitutes"]):
            (substitute_name, position_names) = list(position_data.items())[0]
            self.substitutes.append(Position(idx, substitute_name))
            meta_players = {}
            for position_name in position_names:
                for position in self.positions:
                    if position.name.startswith(position_name):
                        for player in position.players:
                            if player.name not in meta_players:
                                meta_players[player.name] = 0
                            meta_players[player.name] += player.score
            for name, score in meta_players.items():
                self.substitutes[-1].players.append(Player(name, score))

    def construct_candidate_teams(self, min_score, depth, excluded_names):
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

    def construct_candidate_subs(self, min_score, depth, excluded_names):
        allowed = []
        for substitute in self.substitutes:
            allowed_in_position = []
            for player in substitute.players:
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

    def __pick_permutation(self, permutations):
        best_score, best_team = self.penalty, Team([])
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

    def __pick_named_team(self, name, min_score, depth):
        (allowed, n_permutations) = self.construct_candidate_teams(
            min_score, depth, self.excluded_names
        )
        permutations = tqdm.tqdm(
            itertools.product(*allowed),
            total=n_permutations,
            desc=f"Picking {name} team",
        )
        team = self.__pick_permutation(permutations)
        team.summarise(self.positions)
        self.excluded_names += team.names
        return team

    def pick_first_team(self, min_score=0.5, depth=99):
        self.teams["first"] = self.__pick_named_team("first", min_score, depth)
        # self.excluded_names += self.teams["first"].names

    def pick_substitutes(self, min_score=0.0, depth=99):
        (allowed, n_permutations) = self.construct_candidate_subs(
            min_score, depth, self.excluded_names
        )
        permutations = tqdm.tqdm(
            itertools.product(*allowed),
            total=n_permutations,
            desc="Picking substitutes",
        )
        self.teams["subs"] = self.__pick_permutation(permutations)
        self.teams["subs"].summarise(self.substitutes)

    def pick_second_team(self, min_score=0.0, depth=99):
        self.teams["second"] = self.__pick_named_team("second", min_score, depth)
        # self.excluded_names += self.teams["second"].names

    def pick_third_team(self, min_score=0.0, depth=99):
        self.teams["third"] = self.__pick_named_team("third", min_score, depth)
        # self.excluded_names += self.teams["third"].names

    def list_others(self, min_score=0.0, depth=99):
        remaining_names = set()
        excluded_names = sum(
            [
                self.teams[name].names
                for name in ["first", "second", "third"]
                if self.teams[name]
            ],
            [],
        )
        for position in self.positions:
            for player in position.players:
                if player.name not in excluded_names and player.score > 0.0:
                    remaining_names.add(player.name)
        print("Remaining players:")
        for name in sorted(remaining_names):
            print(f"... {name}")
