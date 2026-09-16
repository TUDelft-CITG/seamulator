"""Control components for the maritime traffic visualization."""

from dash import html


def create_control_panel(
    vessel_types: list[str],
) -> html.Div:
    """Create the control panel with information display and refresh button.

    Args:
        vessel_types: List of available vessel types (unused, kept for compatibility).

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
