"""Main Dash application for maritime traffic visualization."""

from datetime import UTC, datetime
from typing import Any

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dcc, html, no_update

from seamulator.data.sample_data import generate_traffic_data
from seamulator.visualization.components.controls import (
    create_control_panel,
    create_info_panel,
    get_all_vessel_types,
)
from seamulator.visualization.components.map import (
    add_vessels_to_map,
    create_base_map,
)

# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# Initial data
initial_vessels = generate_traffic_data(100)

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
                create_control_panel(get_all_vessel_types()),
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
    Input("vessel-count-slider", "value"),
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True,
)
def update_vessel_data(num_vessels: int, n_clicks: int | None) -> list[dict[str, Any]]:
    """Generate new vessel data based on slider value or refresh button."""
    if n_clicks is None:
        raise no_update

    vessels = generate_traffic_data(num_vessels)
    return vessels


@callback(
    Output("vessel-data-store", "data", allow_duplicate=True),
    Input("vessel-count-slider", "value"),
    State("vessel-data-store", "data"),
    prevent_initial_call=True,
)
def update_vessel_data_slider(
    num_vessels: int, current_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Update vessel data when slider changes (not from refresh button)."""
    if len(current_data) == num_vessels:
        raise no_update

    vessels = generate_traffic_data(num_vessels)
    return vessels


@callback(
    Output("traffic-map", "figure"),
    Input("vessel-data-store", "data"),
    Input("vessel-type-filter", "value"),
    Input("map-style", "value"),
    Input("show-labels", "value"),
)
def update_map(
    vessels: list[dict[str, Any]],
    selected_types: list[str] | None,
    map_style: str,
    show_labels: list[str] | None,
) -> go.Figure:
    """Update the traffic map based on current filters and data."""
    if not vessels:
        # Generate default data if empty
        vessels = generate_traffic_data(100)

    if selected_types is None or len(selected_types) == 0:
        selected_types = get_all_vessel_types()

    show_labels_flag = "show" in show_labels if show_labels else False

    # Create the map with the selected style
    fig = create_base_map(map_style)

    # Add vessels
    fig = add_vessels_to_map(fig, vessels, selected_types, show_labels_flag)

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
    Input("vessel-type-filter", "value"),
)
def update_stats(
    vessels: list[dict[str, Any]], selected_types: list[str] | None
) -> str:
    """Update the statistics display."""
    if not vessels:
        return "No vessel data"

    if selected_types and len(selected_types) > 0:
        filtered_vessels = [v for v in vessels if v["type"] in selected_types]
    else:
        filtered_vessels = vessels

    # Count by type
    type_counts = {}
    for v in filtered_vessels:
        vtype = v["type"]
        type_counts[vtype] = type_counts.get(vtype, 0) + 1

    # Calculate statistics
    speeds = [v["speed"] for v in filtered_vessels]
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    max_speed = max(speeds) if speeds else 0

    stats_text = f"""Total Vessels: {len(filtered_vessels)}

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
