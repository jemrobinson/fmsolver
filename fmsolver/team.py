import itertools
import yaml
from .player import Player
from .position import Position

class Team():
    penalty = 9999

    def __init__(self, filename, min_score=0.5):
        with open(filename) as f_input:
            raw_data = yaml.safe_load(f_input)

        self.positions = [Position(idx, name) for idx, name in enumerate(raw_data.keys())]
        self.players = [Player(name) for name in sorted(set([list(d.keys())[0] for d in sum(raw_data.values(), [])]))]
        self.teams = [[0] * len(self.positions), [0] * len(self.positions)]

        for position in self.positions:
            for entry in raw_data[position.name]:
                name, score = list(entry.keys())[0], list(entry.values())[0]
                player = [p for p in self.players if p.name == name][0]
                if score >= min_score:
                    position.players[player] = score

    def score_team(self, selected, penalty_=9999):
        total_score = 0
        selected_player_names = []
        for selection, position in zip(selected, self.positions):
            if selection > position.n_players:
                return penalty_
            else:
                (selected_player, score_) = position.player(selection)
                if selected_player.name in selected_player_names:
                    return penalty_
                else:
                    selected_player_names.append(selected_player.name)
                    total_score += position.max_score - score_
        return total_score

    def populate_team(self, numbers):
        team = []
        for selection, position in zip(numbers, self.positions):
            (selected_player, score_) = position.player(selection)
            team.append((position, selected_player, score_))
        return team

    def summary(self):
        print("** First team **")
        self.summarise_team(0)
        print("** Second team **")
        self.summarise_team(1)

    def summarise_team(self, team):
        total_score, max_score = 0, 0
        for position, selected_player, score_ in self.populate_team(self.teams[team]):
            print(f"... {position.name:<3} {selected_player.name:<15} {score_:.1f}")
            total_score += score_
            max_score += position.max_score
        print(f"Score {total_score} / {max_score}")

    def pick_first_team(self, depth=99):
        best_score = self.penalty
        for selected in itertools.product(*[list(range(min(position.n_players, depth))) for position in self.positions]):
            score_ = self.score_team(selected, self.penalty)
            if score_ < best_score:
                best_score = score_
                self.teams[0] = selected
                if best_score == 0:
                    break
                print("** New best first team! **")
                print(selected)

    def pick_second_team(self, depth=99):
        excluded_names = [p[1].name for p in self.populate_team(self.teams[0])]
        non_excluded = []
        for position in self.positions:
            allowed = []
            for idx in range(position.n_players):
                if position.player(idx)[0].name not in excluded_names:
                    allowed.append(idx)
                    if len(allowed) >= depth:
                        break
            non_excluded.append(allowed)
        best_score = self.penalty
        for selected in itertools.product(*non_excluded):
            score_ = self.score_team(selected, self.penalty)
            if score_ < best_score:
                best_score = score_
                self.second_team = selected
                if best_score == 0:
                    break
                print("** New best second team! **")
                print(selected)
