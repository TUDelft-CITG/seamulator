"""Traffic map component for maritime traffic visualization."""

from typing import Any

import plotly.graph_objects as go
from geopandas import GeoDataFrame

from seamulator.visualization.components.map import create_base_map


def create_triangle_path() -> str:
    """Create SVG path for a triangle marker.

    Returns:
        SVG path string for an equilateral triangle pointing upwards.
    """
    # Triangle with base at bottom, pointing up (north)
    return "M 0 0.5 L -0.5 -0.5 L 0.5 -0.5 Z"


class TrafficMap:
    """A class to manage the traffic map figure and update it efficiently.

    This class maintains a single figure instance and provides methods to
    update vessel positions without recreating the entire figure.
    """

    def __init__(self, title: str = "Maritime Traffic Simulation") -> None:
        """Initialize the traffic map with a base map.

        Args:
            title: The title for the map.
        """
        self.fig = create_base_map()
        self.title = title
        self._vessel_traces: dict[str, int] = {}  # Map type to trace index
        self._density_trace_idx: int | None = None  # Index of density heatmap trace
        self.triangle_path = create_triangle_path()

        # Update layout with title
        self.fig.update_layout(
            title={
                "text": title,
                "x": 0.5,
                "xanchor": "center",
                "y": 0.95,
                "yanchor": "top",
                "font": {"size": 24, "color": "#333"},
            },
            height=900,
        )

    def update_vessels(self, vessels: list[dict[str, Any]]) -> None:
        """Update vessel positions on the map.

        Args:
            vessels: List of vessel dictionaries with lat, lon, heading, etc.
        """
        from seamulator.visualization.components.map import (
            get_vessel_marker_size,
        )

        # Clear existing vessel traces
        # Find all scattermap traces and remove them
        traces_to_remove = []
        for idx, trace in enumerate(self.fig.data):
            if hasattr(trace, "type") and trace.type == "scattermap":
                traces_to_remove.append(idx)

        # Remove traces in reverse order to avoid index shifting
        for idx in sorted(traces_to_remove, reverse=True):
            self.fig.data = self.fig.data[:idx] + self.fig.data[idx + 1 :]

        # Group vessels by type for efficient plotting
        types = set(v["type"] for v in vessels)

        for vessel_type in types:
            type_vessels = [v for v in vessels if v["type"] == vessel_type]

            if not type_vessels:
                continue

            lats = [v["lat"] for v in type_vessels]
            lons = [v["lon"] for v in type_vessels]
            sizes = [get_vessel_marker_size(v["size"]) for v in type_vessels]
            colors = [v["color"] for v in type_vessels]
            names = [v["name"] for v in type_vessels]
            speeds = [v["speed"] for v in type_vessels]
            headings = [v["heading"] for v in type_vessels]
            ports = [v["port"] for v in type_vessels]

            # Create hover text
            hover_texts = [
                f"<b>{name}</b><br>"
                f"Type: {vessel_type}<br>"
                f"Speed: {speed} knots<br>"
                f"Heading: {heading}&deg;<br>"
                f"Size: {size}m<br>"
                f"Near: {port}"
                for name, speed, heading, size, port in zip(
                    names, speeds, headings, [v["size"] for v in type_vessels], ports
                )
            ]

            # Convert compass bearing to plotly angle
            # angles = [90 - h for h in headings]

            self.fig.add_trace(
                go.Scattermap(
                    lat=lats,
                    lon=lons,
                    mode="markers",
                    marker={
                        "size": sizes,
                        "color": colors,
                        # "opacity": 0.8,
                        # "sizemode": "diameter", # Custom symbols do not work
                        # "symbol": [self.triangle_path] * len(lats),
                        # "angle": angles,
                    },
                    name=vessel_type,
                    hovertext=hover_texts,
                    hoverinfo="text",
                    text=names,
                    textposition="top center",
                )
            )

        # Update title with vessel count
        self.fig.update_layout(
            title={
                "text": f"{self.title} ({len(vessels)} vessels)",
                "x": 0.5,
                "xanchor": "center",
                "y": 0.95,
                "yanchor": "top",
                "font": {"size": 24, "color": "#333"},
            }
        )

    def update_density(self, gdf: GeoDataFrame) -> None:
        """Update or add the density heatmap layer using go.Choroplethmap.

        Args:
            gdf: GeoDataFrame with H3 hexagons containing density values.
        """
        # Remove all existing choroplethmap traces
        traces_to_remove = []
        for idx, trace in enumerate(self.fig.data):
            if hasattr(trace, "type") and trace.type == "choroplethmap":
                traces_to_remove.append(idx)

        # Remove traces in reverse order to avoid index shifting
        for idx in sorted(traces_to_remove, reverse=True):
            self.fig.data = self.fig.data[:idx] + self.fig.data[idx + 1 :]

        # Update the density trace index
        self._density_trace_idx = None

        # Skip if GeoDataFrame is empty
        if gdf.empty:
            return

        # Convert GeoDataFrame to GeoJSON for Plotly
        # The GeoJSON features have id=0,1,2,... so we use range(len(gdf)) as locations
        geojson = gdf.__geo_interface__

        # Add choroplethmap trace
        self.fig.add_trace(
            go.Choroplethmap(
                geojson=geojson,
                locations=list(range(len(gdf))),
                z=gdf["density"].tolist(),
                colorscale="Viridis",
                zmin=0,
                zmax=gdf["density"].max() if len(gdf) > 0 else 1,
                marker_line_width=0,
                marker_opacity=0.7,
                hovertemplate=(
                    "<b>H3 Index:</b> %{customdata[0]}<br>"
                    + "<b>Density:</b> %{z:.4f} vessels/km²<br>"
                    + "<b>Vessel Count:</b> %{customdata[1]}<br>"
                    + "<extra></extra>"
                ),
                customdata=[gdf["h3_index"].tolist(), gdf["count"].tolist()],
                name="Vessel Density",
                showscale=True,
            )
        )

        # Store the index of the density trace
        self._density_trace_idx = len(self.fig.data) - 1

    def toggle_density(self) -> None:
        """Toggle the visibility of the density heatmap layer."""
        # Find the density trace
        for idx, trace in enumerate(self.fig.data):
            if hasattr(trace, "type") and trace.type == "choroplethmap":
                # Toggle visibility
                current_visible = trace.visible if hasattr(trace, "visible") else True
                trace.visible = not current_visible
                self._density_trace_idx = idx
                break

    def get_figure(self) -> go.Figure:
        """Get the current figure.

        Returns:
            The current Plotly figure.
        """
        return self.fig
