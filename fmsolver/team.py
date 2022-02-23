import functools
import itertools
import tqdm
import yaml
from .player import Player
from .position import Position

class Team():
    penalty = 9999

    def __init__(self, filename, min_score=0.0):
        with open(filename) as f_input:
            raw_data = yaml.safe_load(f_input)

        self.positions = [Position(idx, name) for idx, name in enumerate(raw_data.keys())]
        self.teams = [[0] * len(self.positions) for _ in range(3)]

        for position in self.positions:
            for entry in raw_data[position.name]:
                name, score = list(entry.keys())[0], list(entry.values())[0]
                if score >= min_score:
                    position.players.append(Player(name, score))
            position.players.append(Player(f"[No {position.name}]", 0.0))

    def score_team(self, indices, penalty_=9999):
        total_score = 0
        player_names = set()
        for idx, position in zip(indices, self.positions):
            if idx > position.n_players:
                return penalty_
            else:
                player = position.player(idx)
                if player.name in player_names:
                    return penalty_
                else:
                    player_names.add(player.name)
                    total_score += position.max_score - player.score
        return total_score

    def get_names(self, numbers):
        team = []
        for idx, position in zip(numbers, self.positions):
            player = position.player(idx)
            team.append((position, player))
        return team

    def summary(self):
        print("** First team **")
        self.summarise_team(0)
        print("** Second team **")
        self.summarise_team(1)
        print("** Third team **")
        self.summarise_team(2)

    def summarise_team(self, team):
        total_score, max_score = 0, 0
        for position, player in self.get_names(self.teams[team]):
            print(f"... {position.name:<3} {player.name:<15} {player.score:.1f}")
            total_score += player.score
            max_score += position.max_score
        print(f"Score {total_score} / {max_score}")

    def construct_allowlists(self, min_score=0.0, depth=99, excluded_names=[]):
        allowed = []
        for position in self.positions:
            allowed_ = []
            for idx in range(position.n_players):
                if len(allowed_) >= depth:
                    continue
                if position.player(idx).score < min_score:
                    continue
                if position.player(idx).name in excluded_names:
                    continue
                allowed_.append(idx)
            allowed.append(allowed_)
        print(f"Considering {functools.reduce(lambda x, y: x * y, [len(a) for a in allowed])} possible permutations")
        return allowed

    def pick_first_team(self, min_score=0.5, depth=99):
        allowed = self.construct_allowlists(min_score=min_score, depth=depth)
        best_score = self.penalty
        for indices in tqdm.tqdm(itertools.product(*allowed)):
            score_ = self.score_team(indices, self.penalty)
            if score_ < best_score:
                best_score = score_
                # print(f"New best first team! {[position.player(idx).name for idx, position in zip(indices, self.positions)]}")
                self.teams[0] = indices
                if best_score == 0:
                    break

    def pick_second_team(self, min_score=0.0, depth=99):
        excluded_names = [p[1].name for p in self.get_names(self.teams[0])]
        allowed = self.construct_allowlists(min_score=min_score, depth=depth, excluded_names=excluded_names)
        best_score = self.penalty
        for indices in tqdm.tqdm(itertools.product(*allowed)):
            score_ = self.score_team(indices, self.penalty)
            if score_ < best_score:
                best_score = score_
                # print(f"New best second team! {[position.player(idx).name for idx, position in zip(indices, self.positions)]}")
                self.teams[1] = indices
                if best_score == 0:
                    break

    def pick_third_team(self, depth=99):
        excluded_names = [p[1].name for idx in range(2) for p in self.get_names(self.teams[idx])]
        allowed = self.construct_allowlists(min_score=0.0, depth=depth, excluded_names=excluded_names)
        best_score = self.penalty
        for indices in tqdm.tqdm(itertools.product(*allowed)):
            score_ = self.score_team(indices, self.penalty)
            if score_ < best_score:
                best_score = score_
                # print(f"New best third team! {[position.player(idx).name for idx, position in zip(indices, self.positions)]}")
                self.teams[2] = indices
                if best_score == 0:
                    break
