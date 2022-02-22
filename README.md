# FM Solver

Simple brute-force team selection solver.
Create an input YAML file with the following format:

```yaml
PositionName1:
  - PlayerName1: PositionScore
  - PlayerName2: PositionScore
PositionName2:
  - PlayerName1: PositionScore
  - PlayerName2: PositionScore
  - PlayerName3: PositionScore
```

Run `python evaluate.py <path to YAML file>` to evaluate the best selections.