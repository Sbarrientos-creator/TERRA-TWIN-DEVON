"""Resumable downloader that records provenance in docs/source_registry.json.
Paste URLs you verified in a browser into FILES."""
import hashlib
import json
import pathlib

import requests


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def fetch(url, dest):
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        tmp = dest.with_suffix(dest.suffix + ".part")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for block in r.iter_content(1 << 20):
                    f.write(block)
        tmp.rename(dest)
    return {"url": url, "file": str(dest), "sha256": sha256_of(dest),
            "bytes": dest.stat().st_size}


# destination path -> verified URL
FILES = {
    # "data/raw/moon/LDEM_80S_xxx.tif": "https://pds-geosciences.wustl.edu/....",
    # "data/raw/mars/mola_dem.tif": "https://....",
    # "data/raw/earth/haughton_arcticdem.tif": "https://....",
}

if __name__ == "__main__":
    if not FILES:
        raise SystemExit("Add verified URLs to FILES first.")
    registry = [fetch(u, d) for d, u in FILES.items()]
    pathlib.Path("docs").mkdir(exist_ok=True)
    json.dump(registry, open("docs/source_registry.json", "w"), indent=2)
    print("Wrote docs/source_registry.json with", len(registry), "files")
