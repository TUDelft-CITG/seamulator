"""Control components for the maritime traffic visualization."""

from dash import dcc, html


def create_control_panel(
    vessel_types: list[str],
) -> html.Div:
    """Create the control panel with filters and settings.

    Args:
        vessel_types: List of available vessel types.

    Returns:
        HTML div containing control components.
    """
    control_panel = html.Div(
        [
            html.Div(
                "Controls",
                style={
                    "fontWeight": "bold",
                    "fontSize": "18px",
                    "padding": "10px",
                    "backgroundColor": "#2c3e50",
                    "color": "white",
                    "borderRadius": "5px 5px 0 0",
                },
            ),
            html.Div(
                [
                    html.Hr(style={"margin": "5px 0", "borderColor": "#ddd"}),
                    # Vessel Type Filter
                    html.Div(
                        [
                            html.Label(
                                "Filter by Vessel Type:",
                                style={
                                    "fontWeight": "bold",
                                    "display": "block",
                                    "marginBottom": "5px",
                                },
                            ),
                            dcc.Checklist(
                                id="vessel-type-filter",
                                options=[
                                    {"label": f"  {vt}", "value": vt}
                                    for vt in vessel_types
                                ],
                                value=vessel_types,
                                inline=False,
                                style={"marginTop": "5px"},
                                labelStyle={
                                    "display": "block",
                                    "marginBottom": "3px",
                                    "cursor": "pointer",
                                },
                            ),
                        ],
                        style={"marginBottom": "15px"},
                    ),
                    html.Hr(style={"margin": "10px 0", "borderColor": "#ddd"}),
                    # Number of Vessels
                    html.Div(
                        [
                            html.Label(
                                "Number of Vessels:",
                                style={
                                    "fontWeight": "bold",
                                    "display": "block",
                                    "marginBottom": "5px",
                                },
                            ),
                            dcc.Slider(
                                id="vessel-count-slider",
                                min=10,
                                max=500,
                                step=10,
                                value=100,
                                marks={
                                    i: str(i) for i in [10, 50, 100, 200, 300, 400, 500]
                                },
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ],
                        style={"marginBottom": "15px"},
                    ),
                    html.Hr(style={"margin": "10px 0", "borderColor": "#ddd"}),
                    # Animation Controls
                    html.Div(
                        [
                            html.Label(
                                "Animation:",
                                style={
                                    "fontWeight": "bold",
                                    "display": "block",
                                    "marginBottom": "5px",
                                },
                            ),
                            html.Div(
                                [
                                    dcc.Checklist(
                                        id="animation-toggle",
                                        options=[
                                            {
                                                "label": " Enable Animation",
                                                "value": "enabled",
                                            }
                                        ],
                                        value=[],
                                        inline=True,
                                        style={"marginBottom": "10px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Speed:",
                                        style={
                                            "fontWeight": "bold",
                                            "marginRight": "10px",
                                        },
                                    ),
                                    dcc.Slider(
                                        id="animation-speed",
                                        min=1,
                                        max=10,
                                        step=1,
                                        value=5,
                                        marks={i: str(i) for i in [1, 5, 10]},
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True,
                                        },
                                    ),
                                ],
                            ),
                        ],
                        style={"marginBottom": "15px"},
                    ),
                    html.Hr(style={"margin": "10px 0", "borderColor": "#ddd"}),
                    # Map Settings
                    html.Div(
                        [
                            html.Label(
                                "Map Style:",
                                style={
                                    "fontWeight": "bold",
                                    "display": "block",
                                    "marginBottom": "5px",
                                },
                            ),
                            dcc.Dropdown(
                                id="map-style",
                                options=[
                                    {
                                        "label": "Open Street Map",
                                        "value": "open-street-map",
                                    },
                                    {
                                        "label": "Stamen Terrain",
                                        "value": "stamen-terrain",
                                    },
                                    {
                                        "label": "Carto Positron",
                                        "value": "carto-positron",
                                    },
                                    {"label": "Dark Matter", "value": "dark-matter"},
                                ],
                                value="open-street-map",
                                clearable=False,
                            ),
                        ],
                        style={"marginBottom": "15px"},
                    ),
                    # Show Labels
                    html.Div(
                        [
                            dcc.Checklist(
                                id="show-labels",
                                options=[
                                    {"label": " Show Vessel Labels", "value": "show"}
                                ],
                                value=[],
                                inline=True,
                            ),
                        ],
                        style={"marginBottom": "15px"},
                    ),
                    html.Hr(style={"margin": "10px 0", "borderColor": "#ddd"}),
                    # Statistics Display
                    html.Div(
                        id="vessel-stats",
                        style={
                            "backgroundColor": "#ecf0f1",
                            "padding": "10px",
                            "borderRadius": "5px",
                            "fontSize": "14px",
                        },
                    ),
                    html.Hr(style={"margin": "10px 0", "borderColor": "#ddd"}),
                    # Refresh Button
                    html.Div(
                        [
                            html.Button(
                                "Refresh Data",
                                id="refresh-button",
                                style={
                                    "width": "100%",
                                    "padding": "8px",
                                    "backgroundColor": "#3498db",
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "4px",
                                    "cursor": "pointer",
                                    "fontSize": "14px",
                                },
                            ),
                        ],
                    ),
                ],
                style={"padding": "10px"},
            ),
        ],
        style={
            "position": "absolute",
            "top": "10px",
            "left": "10px",
            "width": "280px",
            "zIndex": 1000,
            "backgroundColor": "white",
            "borderRadius": "5px",
            "boxShadow": "0 2px 10px rgba(0,0,0,0.2)",
            "fontFamily": "Arial, sans-serif",
        },
    )

    return control_panel


def create_info_panel() -> html.Div:
    """Create the information panel.

    Returns:
        HTML div containing info panel.
    """
    info_panel = html.Div(
        [
            html.Div(
                "Information",
                style={
                    "fontWeight": "bold",
                    "fontSize": "18px",
                    "padding": "10px",
                    "backgroundColor": "#2c3e50",
                    "color": "white",
                    "borderRadius": "5px 5px 0 0",
                },
            ),
            html.Div(
                [
                    html.Div(
                        id="hover-info",
                        style={
                            "minHeight": "100px",
                            "padding": "10px",
                            "backgroundColor": "#ecf0f1",
                            "borderRadius": "5px",
                            "fontSize": "14px",
                        },
                        children="Hover over a vessel to see details",
                    ),
                ],
                style={"padding": "10px"},
            ),
        ],
        style={
            "position": "absolute",
            "bottom": "10px",
            "left": "10px",
            "width": "280px",
            "zIndex": 1000,
            "backgroundColor": "white",
            "borderRadius": "5px",
            "boxShadow": "0 2px 10px rgba(0,0,0,0.2)",
            "fontFamily": "Arial, sans-serif",
        },
    )

    return info_panel


def get_all_vessel_types() -> list[str]:
    """Get list of all vessel types.

    Returns:
        List of vessel type strings.
    """
    return [
        "Cargo",
        "Tanker",
        "Container",
        "Bulk",
        "Passenger",
        "Fishing",
        "Tug",
        "Other",
    ]
