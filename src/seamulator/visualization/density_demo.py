"""Standalone Dash app to demonstrate density heatmap visualization.

This script creates a simple Dash application that displays a TrafficMap
with a pre-made density heatmap using sample vessel positions.
"""

from dash import Dash, dcc, html

from seamulator.simulation.density_heatmap import DensityHeatmap
from seamulator.visualization.components.traffic_map import TrafficMap

# Sample vessel positions in the North Sea region
SAMPLE_VESSEL_POSITIONS = [
    # Amsterdam area
    (52.3676, 4.9041),
    (52.3700, 4.9100),
    (52.3650, 4.9000),
    (52.3750, 4.9150),
    # Rotterdam area
    (51.9225, 4.4792),
    (51.9200, 4.4800),
    (51.9300, 4.4900),
    # Hamburg area
    (53.5503, 9.9932),
    (53.5550, 10.0000),
    (53.5450, 9.9850),
    # Antwerp area
    (51.2194, 4.4024),
    (51.2200, 4.4050),
    (51.2150, 4.3980),
    # More vessels in clustered areas
    (52.3680, 4.9050),
    (52.3690, 4.9060),
    (52.3700, 4.9070),
    (51.9230, 4.4800),
    (51.9240, 4.4810),
    (53.5510, 9.9940),
    (53.5520, 9.9950),
]


def create_density_demo_app() -> Dash:
    """Create a Dash app with a TrafficMap and density heatmap.

    Returns:
        A Dash application instance.
    """
    # Initialize the traffic map
    traffic_map = TrafficMap(title="Vessel Density Heatmap Demo")

    # Create sample density heatmap with finer resolution
    density_heatmap = DensityHeatmap(resolution=7)
    density_heatmap.calculate_density(SAMPLE_VESSEL_POSITIONS)
    density_gdf = density_heatmap.get_geometry()
    traffic_map.update_density(density_gdf)

    # Create the Dash app
    app = Dash(__name__, suppress_callback_exceptions=True)

    # App layout
    app.layout = html.Div(
        [
            dcc.Graph(
                id="density-map",
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                },
                style={"width": "100vw", "height": "100vh"},
                figure=traffic_map.get_figure(),
            ),
        ],
        style={"margin": 0, "padding": 0, "height": "100vh", "width": "100vw"},
    )

    return app


def main():
    """Run the density heatmap demo application."""
    app = create_density_demo_app()
    app.run(debug=True, host="0.0.0.0", port=8051)


if __name__ == "__main__":
    main()
