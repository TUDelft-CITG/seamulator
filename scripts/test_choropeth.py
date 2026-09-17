import json
from urllib.request import urlopen

import plotly.graph_objects as go

with urlopen(
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
) as response:
    counties = json.load(response)

import pandas as pd

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
    dtype={"fips": str},
)


fig = go.Figure(
    go.Choroplethmap(
        geojson=counties,
        locations=df.fips,
        z=df.unemp,
        colorscale="Viridis",
        zmin=0,
        zmax=12,
        marker_opacity=0.5,
        marker_line_width=0,
    )
)
fig.update_layout(
    map_style="carto-positron", map_zoom=3, map_center={"lat": 37.0902, "lon": -95.7129}
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
