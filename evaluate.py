#! /usr/bin/env python
import argparse
from fmsolver import Team

def main(input_file):
    team = Team(input_file, min_score=2.5)
    team.pick_first_team()
    team.pick_second_team()
    team.summary()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input YAML file")
    args = parser.parse_args()
    main(args.input)