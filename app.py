import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analog import GROUPS, score
from src.targets import TARGETS

st.set_page_config(layout="wide")
st.title("Terrestrial Analog Finder")
st.caption("Ranks Earth locations by similarity to a lunar or Martian target. "
           "Earth cannot replicate vacuum, gravity or radiation.")

earth = pd.read_csv("data/processed/earth_features.csv")
name = st.sidebar.selectbox("Target", list(TARGETS))
w = {g: st.sidebar.slider(f"Weight: {g}", 0.0, 1.0, 1.0) for g in GROUPS}
target = TARGETS[name]
if any(v is None for v in target.values()):
    st.error("Fill the target values (terrain and Diviner/THEMIS thermal) in src/targets.py")
    st.stop()

res = score(earth, target, w)
top = res.head(int(st.sidebar.number_input("Top N", 10, 500, 50)))

fig = px.scatter_geo(top, lat="lat", lon="lon", color="sim_total", size="sim_total",
                     hover_data=["slope_deg", "roughness_m", "temp_mean_C",
                                 "diurnal_range_C", "precip_mm", "ndvi"],
                     color_continuous_scale="Viridis", projection="natural earth")
st.plotly_chart(fig, use_container_width=True)

pick = st.selectbox("Characterize site", top.index,
                    format_func=lambda i: f"{top.lon[i]:.2f}, {top.lat[i]:.2f}")
row = top.loc[pick]
radar = go.Figure(go.Scatterpolar(r=[row[f"sim_{g}"] for g in GROUPS],
                                  theta=list(GROUPS), fill="toself"))
radar.update_polars(radialaxis=dict(range=[0, 1]))
st.plotly_chart(radar)
st.dataframe(top)

st.subheader("Data sources and limitations")
st.markdown(
    "- Earth: Copernicus GLO-30 DEM, MODIS LST/NDVI, CHIRPS (see docs/DATA_SOURCES.md)\n"
    "- Moon/Mars targets: LOLA, MOLA, Diviner, THEMIS\n"
    "- Scores compare listed factors only, not overall planetary similarity.")
