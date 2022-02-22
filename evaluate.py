#! /usr/bin/env python
import argparse
from fmsolver import Team

def main(input_file):
    team = Team(input_file)
    team.pick_first_team(min_score=3)
    team.pick_second_team(min_score=1.5)
    team.pick_third_team()
    team.summary()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input YAML file")
    args = parser.parse_args()
    main(args.input)