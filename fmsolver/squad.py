import functools
import itertools
from math import perm
import tqdm
import yaml
from .player import Player
from .position import Position
from .team import Team


class Squad:
    def __init__(self, filename, exclude=[], min_score=0.0):
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
            for _ in range(3):
                position.players.append(Player(f"[No {position.name}]", 0.0))

        for idx, position_data in enumerate(raw_data["substitutes"]):
            (substitute_name, position_names) = list(position_data.items())[0]
            self.substitutes.append(Position(idx, substitute_name))
            meta_players = {}
            for position_name in position_names:
                for position in self.positions:
                    if position.name.startswith(f"{position_name}_"):
                        for player in position.players:
                            if player.name not in meta_players:
                                meta_players[player.name] = 0
                            meta_players[player.name] += player.score
            for name, score in meta_players.items():
                self.substitutes[-1].players.append(Player(name, score))

    def construct_candidate_teams(self):
        allowed = []
        for position in self.positions:
            allowed_in_position = [
                p for p in position.players if p.name not in self.excluded_names
            ]
            allowed.append(
                sorted(allowed_in_position, key=lambda p: p.score, reverse=True)
            )
        return self.reduced_combinations(allowed)

    def construct_candidate_subs(self):
        allowed = []
        for substitute in self.substitutes:
            allowed_in_position = [
                p for p in substitute.players if p.name not in self.excluded_names
            ]
            allowed.append(
                sorted(allowed_in_position, key=lambda p: p.score, reverse=True)
            )
        return self.reduced_combinations(allowed)

    def reduced_combinations(self, allowed, max_combinations=30000000):
        def get_permutations(player_list):
            return functools.reduce(lambda x, y: x * y, [len(a) for a in player_list])

        while get_permutations(allowed) > max_combinations:
            limit = max([len(position) for position in allowed]) - 1
            allowed = [position[:limit] for position in allowed]
        return (allowed, get_permutations(allowed))

    def __pick_permutation(self, permutations):
        best_score, best_team = 9999, Team([])
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

    def __pick_named_team(self, name):
        (allowed, n_permutations) = self.construct_candidate_teams()
        permutations = tqdm.tqdm(
            itertools.product(*allowed),
            total=n_permutations,
            desc=f"Picking {name} team",
        )
        team = self.__pick_permutation(permutations)
        team.summarise(self.positions)
        self.excluded_names += team.names
        return team

    def pick_first_team(self):
        self.teams["first"] = self.__pick_named_team("first")

    def pick_substitutes(self):
        (allowed, n_permutations) = self.construct_candidate_subs()
        permutations = tqdm.tqdm(
            itertools.product(*allowed),
            total=n_permutations,
            desc="Picking substitutes",
        )
        self.teams["subs"] = self.__pick_permutation(permutations)
        self.teams["subs"].summarise(self.substitutes)

    def pick_second_team(self):
        self.teams["second"] = self.__pick_named_team("second")

    def pick_third_team(self):
        self.teams["third"] = self.__pick_named_team("third")

    def list_others(self):
        remaining_names = set()
        excluded_names = sum([team.names for team in self.teams.values()], [])
        for position in self.positions:
            for player in position.players:
                if player.name not in excluded_names and player.score > 0.0:
                    remaining_names.add(player.name)
        print("Remaining players:")
        for name in sorted(remaining_names):
            print(f"... {name}")
