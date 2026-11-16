import tempfile

import pandas as pd
import plotly.express as px
import streamlit as st

from src.similarity import compare
from src.terrain import analyze, load_window

st.set_page_config(page_title="TERRA-TWIN DEVON", layout="wide")
st.title("TERRA-TWIN DEVON ANALYZER")
st.caption("Terrain-morphology comparison. Not a measure of overall planetary similarity.")

SITES = {  # lon (deg E), lat (deg N): verify before use
    "earth": ("Haughton Crater", -89.67, 75.22),
    "moon": ("Shackleton Crater", 0.0, -89.9),
    "mars": ("Mars crater (edit me)", 207.8, 23.3),
}

st.sidebar.header("1. Upload DEMs (GeoTIFF)")
files = {b: st.sidebar.file_uploader(f"{b.title()} DEM", type=["tif", "tiff"], key=b)
         for b in SITES}
st.sidebar.header("2. Settings")
target = st.sidebar.selectbox("Planetary target", ["moon", "mars"])
size_km = st.sidebar.slider("Window size (km)", 10, 60, 30)
res_m = st.sidebar.select_slider("Common resolution (m)", [50, 100, 250, 500], 100)
coords = {}
for b, (name, lon, lat) in SITES.items():
    c1, c2 = st.sidebar.columns(2)
    coords[b] = (c1.number_input(f"{b} lon", value=lon, key=f"lo{b}"),
                 c2.number_input(f"{b} lat", value=lat, key=f"la{b}"))


def run(body):
    f = files[body]
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as t:
        t.write(f.getbuffer())
    z, r, meta = load_window(t.name, body, *coords[body], size_km, res_m)
    layers, stats = analyze(z, r)
    return layers, stats, meta


if files["earth"] and files[target] and st.button("Run analysis"):
    with st.spinner("Processing..."):
        la, sa, ma = run("earth")
        lb, sb, mb = run(target)
    st.subheader("Terrain statistics")
    st.dataframe(pd.DataFrame({
        "Devon": {f"{v}.{k}": x for v, d in sa.items() for k, x in d.items()},
        target.title(): {f"{v}.{k}": x for v, d in sb.items() for k, x in d.items()}}))
    st.subheader("Similarity (terrain-distribution overlap only)")
    st.dataframe(pd.DataFrame(compare(la, lb)))
    var = st.selectbox("Variable", list(la))
    df = pd.concat([pd.DataFrame({"value": la[var][::50], "body": "Devon"}),
                    pd.DataFrame({"value": lb[var][::50], "body": target.title()})])
    st.plotly_chart(px.histogram(df, x="value", color="body", barmode="overlay",
                                 histnorm="probability density", nbins=60),
                    use_container_width=True)
    st.subheader("Data provenance")
    st.json({"devon": ma, target: mb})
else:
    st.info("Upload the Devon DEM and one target DEM, then press Run.")
