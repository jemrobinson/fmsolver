#! /usr/bin/env python
import argparse
from fmsolver import Squad

def main(input_file, exclude, n_subs):
    squad = Squad(input_file, exclude, n_subs)
    squad.pick_first_team(depth=6, min_score=2.5)
    squad.pick_substitutes()
    squad.pick_second_team(depth=6, min_score=1.5)
    squad.pick_third_team(depth=6, min_score=1)
    squad.list_others()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input YAML file")
    parser.add_argument("--exclude", nargs="+", default=[], help="Input YAML file")
    parser.add_argument("--subs", help="Number of substitutes", type=int, default=7)
    args = parser.parse_args()
    main(args.input, args.exclude, args.subs)
