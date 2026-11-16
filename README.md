# TERRA-TWIN DEVON

Terrain-morphology comparison of Devon Island (Haughton Crater) with lunar and Martian
targets, plus a Terrestrial Analog Finder that ranks Earth locations by similarity to a
Moon or Mars target using open NASA and other space-agency data.

This is a working draft. The code has not been run on real data yet, so expect small
fixes (dataset IDs, file names) on the first run.

## Design

- `pipeline/` runs offline: downloads data, computes features, writes small files.
- `app.py` and `devon_app.py` (Streamlit) only read `data/processed/` or uploaded files.
- Never commit passwords, `.env`, key files or large `.tif` files.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
earthengine authenticate
cp .env.example .env             # fill in your own values, never commit .env
```

Then export the variables from `.env` into your shell (or set `GEE_PROJECT` directly):

```bash
export GEE_PROJECT=your-cloud-project-id
```

## Run

```bash
pytest                                   # tests on synthetic terrain
python pipeline/00_check_setup.py        # check accounts and dataset IDs
python pipeline/02_earth_features.py 50  # small test run first
python pipeline/03_check_features.py
python pipeline/04_validate.py           # rank known analog sites
streamlit run app.py                     # Analog Finder
streamlit run devon_app.py               # Devon DEM analyzer (upload GeoTIFFs)
```

## Team ownership (one owner per file avoids merge conflicts)

| Area | Owner |
|---|---|
| `src/`, `tests/` | Python Developer |
| `app.py`, `devon_app.py` | Application Developer |
| `pipeline/01_download.py`, `docs/DATA_SOURCES.md` | GIS Specialist |
| `docs/METHODOLOGY.md` | Planetary Science Researcher |
| `docs/VALIDATION.md` | Validation and Presentation |
