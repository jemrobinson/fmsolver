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

## Download missing real faces

```bash
python download.py \
  --rtf ~/OneDrive/Personal/Documents/games/FM21/JamesRobinson.Venezia.real.2025-10-17.rtf \
  --xml ~/OneDrive/Personal/Documents/games/FM21/sortitoutsi/config.xml \
  --target ~/OneDrive/Personal/Documents/games/FM21/sortitoutsi/faces
```

## Generate new RTF for missing newgen faces

```bash
python missing.py \
  --rtf ~/OneDrive/Personal/Documents/games/FM21/JamesRobinson.Venezia.newgens.2025-10-17.rtf \
  --players ~/OneDrive/Personal/Documents/games/FM21/sortitoutsi/config.xml \
  --xml ~/OneDrive/Personal/Documents/games/FM21/fmnewgan/config.xml \
  --out ~/OneDrive/Personal/Documents/games/FM21/fmnewgan/missing-newgens.rtf
```
