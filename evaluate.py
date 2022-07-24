#! /usr/bin/env python
import argparse
from fmsolver import Squad


def main(input_file, exclude, generate_all_teams):
    squad = Squad(input_file, exclude)
    squad.pick_first_team()
    if generate_all_teams:
        squad.pick_second_team()
        squad.pick_third_team()
        squad.list_others()
    else:
        squad.pick_substitutes()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input YAML file")
    parser.add_argument("--exclude", nargs="+", default=[], help="Input YAML file")
    parser.add_argument("--all", help="Generate all teams", action="store_true")
    args = parser.parse_args()
    main(args.input, args.exclude, args.all)
