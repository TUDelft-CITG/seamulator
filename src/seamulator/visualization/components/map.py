"""Map visualization component for maritime traffic."""

from typing import Any

import plotly.express as px
import plotly.graph_objects as go


def create_triangle_path() -> str:
    """Create SVG path for a triangle marker.

    Returns:
        SVG path string for an equilateral triangle pointing upwards.
    """
    # Triangle with base at bottom, pointing up (north)
    # Coordinates: top (0,1), bottom-left (-0.5,-0.5), bottom-right (0.5,-0.5)
    # Normalized to fit in a 1x1 box
    return "M 0 0.5 L -0.5 -0.5 L 0.5 -0.5 Z"


# Mapbox access token (using public token for basic functionality)
# MAPBOX_TOKEN = (
#     "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6Im5rbXl5ZzI2MzIxbnAifQ.T62qn4tY92LLjQ92XxHJg"
# )


def create_base_map(style: str = "open-street-map") -> go.Figure:
    """Create a base map figure with Mapbox style.

    Args:
        style: Map style to use (e.g., 'open-street-map', 'stamen-terrain').

    Returns:
        Plotly figure with map configured.
    """
    fig = go.Figure()

    fig.update_layout(
        map={
            "style": style,
            "center": {"lat": 55, "lon": 5},
            "zoom": 5,
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=True,
        legend={
            "x": 0.01,
            "y": 0.99,
            "bgcolor": "rgba(255,255,255,0.8)",
        },
    )

    return fig


def get_vessel_marker_size(vessel_size: float) -> float:
    """Convert vessel size in meters to marker size for visualization.

    Args:
        vessel_size: Size of vessel in meters.

    Returns:
        Marker size for plotly.
    """
    # Scale: 10m -> 5px, 300m -> 25px, linear scaling
    # size = (vessel_size - 10) * (25 - 5) / (300 - 10) + 5
    # size = (vessel_size - 10) * 20 / 290 + 5
    if vessel_size <= 10:
        return 5
    elif vessel_size >= 300:
        return 25
    else:
        return (vessel_size - 10) * 20 / 290 + 5


def add_vessels_to_map(
    fig: go.Figure,
    vessels: list[dict[str, Any]],
    selected_types: list[str] | None = None,
    show_labels: bool = False,
) -> go.Figure:
    """Add vessels to the map.

    Args:
        fig: Plotly figure to add vessels to.
        vessels: List of vessel dictionaries.
        selected_types: Optional list of vessel types to display (None = all).
        show_labels: Whether to show vessel names as labels.

    Returns:
        Updated figure with vessels.
    """
    if selected_types:
        vessels = [v for v in vessels if v["type"] in selected_types]

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

        # Use custom triangle markers with rotation based on heading
        # Convert compass bearing (0=N, 90=E) to plotly angle (0=E, 90=N)
        angles = [90 - h for h in headings]
        triangle_path = create_triangle_path()

        fig.add_trace(
            go.Scattermap(
                lat=lats,
                lon=lons,
                mode="markers",
                marker={
                    "size": sizes,
                    "color": colors,
                    "opacity": 0.8,
                    "sizemode": "diameter",
                    "symbol": [triangle_path] * len(lats),
                    "angle": angles,
                },
                name=vessel_type,
                hovertext=hover_texts,
                hoverinfo="text",
                text=names if show_labels else None,
                textposition="top center",
            )
        )

    return fig


def add_vessel_tracks(
    fig: go.Figure,
    tracks: dict[str, list[tuple[float, float]]],
    track_colors: dict[str, str] | None = None,
) -> go.Figure:
    """Add vessel tracks (paths) to the map.

    Args:
        fig: Plotly figure.
        tracks: Dictionary mapping vessel names to list of (lat, lon) coordinates.
        track_colors: Optional color mapping for tracks.

    Returns:
        Updated figure with tracks.
    """
    default_colors = px.colors.qualitative.Plotly

    for idx, (vessel_name, coordinates) in enumerate(tracks.items()):
        lats, lons = zip(*coordinates) if coordinates else ([], [])

        color = track_colors.get(vessel_name, default_colors[idx % len(default_colors)])

        fig.add_trace(
            go.Scattermap(
                lat=list(lats),
                lon=list(lons),
                mode="lines",
                line={"width": 2, "color": color, "opacity": 0.5},
                name=f"{vessel_name} track",
                showlegend=False,
            )
        )

    return fig


def create_traffic_map(
    vessels: list[dict[str, Any]],
    selected_types: list[str] | None = None,
    show_labels: bool = False,
    map_style: str = "open-street-map",
) -> go.Figure:
    """Create a complete traffic map with vessels.

    Args:
        vessels: List of vessel dictionaries.
        selected_types: Optional filter for vessel types.
        show_labels: Whether to show vessel name labels.
        map_style: Map style to use.

    Returns:
        Complete plotly figure ready for display.
    """
    fig = create_base_map(map_style)
    fig = add_vessels_to_map(fig, vessels, selected_types, show_labels)

    fig.update_layout(
        title={
            "text": "Maritime Traffic Visualization",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.95,
            "yanchor": "top",
            "font": {"size": 24, "color": "#333"},
        },
        height=900,
    )

    return fig
