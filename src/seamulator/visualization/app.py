"""Main Dash application for maritime traffic visualization."""

from datetime import UTC, datetime
from typing import Any

import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

from seamulator.core.logging_config import logger
from seamulator.simulation.simulation import MaritimeSimulation
from seamulator.visualization.components.controls import (
    create_control_panel,
    create_info_panel,
)
from seamulator.visualization.components.traffic_map import TrafficMap

# Global settings
NUM_VESSELS = 100
TIME_INTERVAL = 100

# Initialize the simulation backend
simulation = MaritimeSimulation(num_vessels=NUM_VESSELS)
simulation.pause()

# Initialize the traffic map
traffic_map = TrafficMap()

# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# App layout
app.layout = html.Div(
    [
        # Store for last update
        dcc.Store(id="last-update", data=datetime.now(UTC).isoformat()),
        # Interval for auto-update when playing
        # Map container
        html.Div(
            [
                dcc.Interval(
                    id="simulation-interval", interval=TIME_INTERVAL, n_intervals=0
                ),
                dcc.Graph(
                    id="traffic-map",
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    },
                    style={"width": "100vw", "height": "100vh"},
                    figure=traffic_map.get_figure(),
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


def update_simulation_stats() -> str:
    """Generate statistics text from simulation state."""
    state = simulation.get_state()
    vessels = state["vessels"]

    if not vessels:
        return "No vessel data"

    # Count by type
    type_counts = {}
    speeds = []
    for vessel_id, vessel in vessels.items():
        v = simulation.get_vessel(vessel_id)
        vtype = v["vessel_type"]
        type_counts[vtype] = type_counts.get(vtype, 0) + 1
        speeds.append(v["speed"])

    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    max_speed = max(speeds) if speeds else 0

    stats_text = f"""Total Vessels: {len(vessels)}
Time: {state["time"]:.1f} hours
Simulation: {"Running" if state["is_running"] else "Paused"}

By Type:
"""

    for vtype, count in sorted(type_counts.items()):
        stats_text += f"    {vtype}: {count}\n"

    stats_text += f"""Average Speed: {avg_speed:.1f} knots
Max Speed: {max_speed:.1f} knots"""

    return stats_text.strip()


@callback(
    Output("traffic-map", "figure"),
    Output("vessel-stats", "children"),
    Output("simulation-interval", "disabled"),
    Input("simulation-interval", "n_intervals"),
    Input("play-button", "n_clicks"),
    Input("pause-button", "n_clicks"),
    Input("step-button", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("last-update", "data"),
    prevent_initial_call=True,
)
def update_simulation(
    n_intervals: int | None,
    play_clicks: int | None,
    pause_clicks: int | None,
    step_clicks: int | None,
    reset_clicks: int | None,
    last_update: str | None,
) -> tuple[go.Figure, str]:
    """Update simulation state and map display."""
    from dash import callback_context

    logger.debug("Update simulation callback triggered")
    disabled = False
    # Determine which button was clicked
    if not callback_context.triggered:
        # Initial load - just display current state
        logger.debug("Initial load, displaying current state")
        pass
    else:
        trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        logger.debug(f"Triggered by: {trigger_id}")

        if trigger_id == "play-button":
            logger.debug("Play button clicked")
            simulation.start()
        elif trigger_id == "pause-button":
            logger.debug("Pause button clicked")
            disabled = True
            simulation.pause()
        elif trigger_id == "step-button":
            logger.debug("Step button clicked")
            simulation.step(time_delta=1.0)
        elif trigger_id == "reset-button":
            logger.debug("Reset button clicked")
            simulation.reset()
            simulation.pause()

    # If simulation is running, step forward on interval
    if simulation.get_state()["is_running"]:
        logger.debug("Simulation is running, stepping forward")
        simulation.step(time_delta=1.0)

    # Get current vessel positions and update the map
    logger.debug("Getting vessel positions")
    vessels = simulation.get_vessel_positions()
    logger.debug(f"Updating traffic map with {len(vessels)} vessels")
    traffic_map.update_vessels(vessels)

    # Update stats
    stats_text = update_simulation_stats()

    return traffic_map.get_figure(), stats_text, disabled


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
