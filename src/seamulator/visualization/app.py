"""Main Dash application for maritime traffic visualization."""

from datetime import UTC, datetime
from typing import Any

import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

from seamulator.data.sample_data import generate_traffic_data
from seamulator.visualization.components.controls import (
    create_control_panel,
    create_info_panel,
)
from seamulator.visualization.components.map import (
    add_vessels_to_map,
    create_base_map,
)

# Global settings
NUM_VESSELS = 100

# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# Initial data
initial_vessels = generate_traffic_data(NUM_VESSELS)

# App layout
app.layout = html.Div(
    [
        # Store for vessel data
        dcc.Store(id="vessel-data-store", data=initial_vessels),
        dcc.Store(id="last-refresh", data=datetime.now(UTC).isoformat()),
        # Map container
        html.Div(
            [
                dcc.Graph(
                    id="traffic-map",
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    },
                    style={"width": "100vw", "height": "100vh"},
                ),
                # Control Panel
                create_control_panel([]),
                # Info Panel
                create_info_panel(),
                # Hidden div for hover info
                html.Div(id="hover-data", style={"display": "none"}),
            ],
            style={"position": "relative", "width": "100vw", "height": "100vh"},
        ),
    ],
    style={"margin": 0, "padding": 0, "height": "100vh", "width": "100vw"},
)


@callback(
    Output("vessel-data-store", "data"),
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_vessel_data(n_clicks: int | None) -> list[dict[str, Any]]:
    """Generate new vessel data when refresh button is clicked."""
    vessels = generate_traffic_data(NUM_VESSELS)
    return vessels


@callback(
    Output("traffic-map", "figure"),
    Input("vessel-data-store", "data"),
)
def update_map(vessels: list[dict[str, Any]]) -> go.Figure:
    """Update the traffic map with current vessel data."""
    if not vessels:
        # Generate default data if empty
        vessels = generate_traffic_data(NUM_VESSELS)

    # Create the map with default style
    fig = create_base_map()

    # Add all vessels without filtering
    fig = add_vessels_to_map(fig, vessels)

    # Update layout
    fig.update_layout(
        title={
            "text": f"Maritime Traffic Visualization ({len(vessels)} vessels)",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.95,
            "yanchor": "top",
            "font": {"size": 24, "color": "#333"},
        },
        height=900,
    )

    return fig


@callback(
    Output("vessel-stats", "children"),
    Input("vessel-data-store", "data"),
)
def update_stats(vessels: list[dict[str, Any]]) -> str:
    """Update the statistics display."""
    if not vessels:
        return "No vessel data"

    # Count by type
    type_counts = {}
    for v in vessels:
        vtype = v["type"]
        type_counts[vtype] = type_counts.get(vtype, 0) + 1

    # Calculate statistics
    speeds = [v["speed"] for v in vessels]
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    max_speed = max(speeds) if speeds else 0

    stats_text = f"""Total Vessels: {len(vessels)}

By Type:
"""

    for vtype, count in sorted(type_counts.items()):
        stats_text += f"    {vtype}: {count}\n"

    stats_text += f"""Average Speed: {avg_speed:.1f} knots
Max Speed: {max_speed:.1f} knots"""

    return stats_text.strip()


@callback(
    Output("hover-info", "children"),
    Input("traffic-map", "hoverData"),
)
def update_hover_info(hover_data: dict[str, Any] | None) -> str:
    """Update the hover info panel."""
    if hover_data is None:
        return "Hover over a vessel to see details"

    # Extract information from hover data
    points = hover_data.get("points", [])
    if not points:
        return "Hover over a vessel to see details"

    point = points[0]
    hover_text = point.get("hovertext", "No details available")

    return hover_text


def main():
    """Run the Dash application."""
    app.run(debug=True, host="0.0.0.0", port=8050)


if __name__ == "__main__":
    main()
