"""Check whether known analog sites rank highly for a target. Report failures honestly."""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.analog import GROUPS, score  # noqa: E402
from src.targets import TARGETS  # noqa: E402

KNOWN = {  # (lon, lat), approximate: confirm coordinates
    "Haughton": (-89.67, 75.22), "Atacama": (-69.2, -24.5),
    "Death Valley": (-116.9, 36.5), "Dry Valleys": (161.5, -77.5),
}


def rank_of_known(scored, known, radius_deg=1.5):
    ranks = {}
    for name, (lon, lat) in known.items():
        near = scored[(abs(scored.lon - lon) < radius_deg) & (abs(scored.lat - lat) < radius_deg)]
        ranks[name] = (int(near.index.min()) + 1 if len(near) else None, len(scored))
    return ranks


if __name__ == "__main__":
    earth = pd.read_csv("data/processed/earth_features.csv")
    for name, target in TARGETS.items():
        if any(v is None for v in target.values()):
            print(f"Skipping {name}: fill its values in src/targets.py")
            continue
        res = score(earth, target, {g: 1.0 for g in GROUPS})
        print(name, rank_of_known(res, KNOWN))
