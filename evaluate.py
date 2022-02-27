#! /usr/bin/env python
import argparse
from fmsolver import Squad

def main(input_file, exclude):
    squad = Squad(input_file, exclude)
    squad.pick_first_team(depth=5)
    squad.pick_second_team()
    squad.pick_third_team()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input YAML file")
    parser.add_argument("--exclude", nargs="+", default=[], help="Input YAML file")
    args = parser.parse_args()
    main(args.input, args.exclude)
