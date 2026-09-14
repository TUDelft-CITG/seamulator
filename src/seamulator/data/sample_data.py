"""Sample maritime traffic data generator."""

from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

# Vessel types with their typical sizes (in meters) and colors
VESSEL_TYPES = {
    "Cargo": {"size": 150, "color": "#FF6B6B", "icon": "ship"},
    "Tanker": {"size": 200, "color": "#4ECDC4", "icon": "oil"},
    "Container": {"size": 250, "color": "#45B7D1", "icon": "cube"},
    "Bulk": {"size": 180, "color": "#FFA07A", "icon": "cube"},
    "Passenger": {"size": 120, "color": "#95E1D3", "icon": "users"},
    "Fishing": {"size": 30, "color": "#A8E6CF", "icon": "fish"},
    "Tug": {"size": 25, "color": "#FFD93D", "icon": "anchor"},
    "Other": {"size": 50, "color": "#BCBD22", "icon": "question"},
}

# Major port coordinates (lat, lon)
PORTS = {
    "Rotterdam": (51.9225, 4.4792),
    "Shanghai": (31.2304, 121.4737),
    "Singapore": (1.3521, 103.8198),
    "Hong Kong": (22.3193, 114.1694),
    "Antwerp": (51.2194, 4.4022),
    "Los Angeles": (33.7128, -118.2707),
    "Hamburg": (53.5511, 9.9937),
    "Dubai": (25.2048, 55.2708),
    "New York": (40.6892, -74.0445),
    "Tokyo": (35.6895, 139.6917),
}


def generate_vessel_name(vessel_type: str, index: int) -> str:
    """Generate a vessel name based on type and index."""
    prefixes = {
        "Cargo": "MV Cargo",
        "Tanker": "MT",
        "Container": "MSC",
        "Bulk": "MV Bulk",
        "Passenger": "MS",
        "Fishing": "FV",
        "Tug": "Tug",
        "Other": "Vessel",
    }
    prefix = prefixes.get(vessel_type, "Vessel")
    return f"{prefix}-{index:04d}"


def generate_random_vessel() -> dict[str, Any]:
    """Generate a single random vessel with all attributes."""
    vessel_type = np.random.choice(list(VESSEL_TYPES.keys()))
    vessel_info = VESSEL_TYPES[vessel_type]

    # Random position near a port
    port_name = np.random.choice(list(PORTS.keys()))
    port_lat, port_lon = PORTS[port_name]

    # Add random offset from port (up to 2 degrees)
    lat_offset = np.random.uniform(-1.5, 1.5)
    lon_offset = np.random.uniform(-1.5, 1.5)

    lat = port_lat + lat_offset
    lon = port_lon + lon_offset

    # Ensure valid latitude range
    lat = np.clip(lat, -89.9, 89.9)

    return {
        "name": generate_vessel_name(vessel_type, np.random.randint(1000, 9999)),
        "type": vessel_type,
        "lat": round(float(lat), 6),
        "lon": round(float(lon), 6),
        "speed": round(float(np.random.uniform(0, 25)), 1),  # knots
        "heading": int(np.random.uniform(0, 360)),  # degrees
        "timestamp": datetime.now(UTC).isoformat(),
        "size": vessel_info["size"],
        "color": vessel_info["color"],
        "port": port_name,
        "mmsi": np.random.randint(
            200000000, 300000000
        ),  # Maritime Mobile Service Identity
    }


def generate_traffic_data(num_vessels: int = 100) -> list[dict[str, Any]]:
    """Generate sample maritime traffic data.

    Args:
        num_vessels: Number of vessels to generate.

    Returns:
        List of vessel dictionaries with position, type, and metadata.
    """
    vessels = []
    for i in range(num_vessels):
        vessel = generate_random_vessel()
        vessels.append(vessel)
    return vessels


def generate_animated_traffic(
    num_vessels: int = 50, num_frames: int = 24, hours_between_frames: int = 1
) -> list[list[dict[str, Any]]]:
    """Generate animated traffic data for simulation.

    Args:
        num_vessels: Number of vessels.
        num_frames: Number of time frames.
        hours_between_frames: Hours between each frame.

    Returns:
        List of lists, where each inner list contains vessel data for a time frame.
    """
    frames = []
    base_time = datetime.now(UTC)

    # Generate initial positions
    vessels = [generate_random_vessel() for _ in range(num_vessels)]

    for frame_idx in range(num_frames):
        frame_time = base_time + timedelta(hours=hours_between_frames * frame_idx)
        frame_vessels = []

        for vessel in vessels:
            # Simulate movement: slight random drift
            lat_drift = np.random.uniform(-0.1, 0.1)
            lon_drift = np.random.uniform(-0.1, 0.1)

            new_vessel = vessel.copy()
            new_vessel["lat"] = round(float(vessel["lat"] + lat_drift), 6)
            new_vessel["lon"] = round(float(vessel["lon"] + lon_drift), 6)
            new_vessel["timestamp"] = frame_time.isoformat()
            new_vessel["heading"] = (
                vessel["heading"] + int(np.random.uniform(-5, 5))
            ) % 360
            new_vessel["speed"] = round(
                float(np.clip(vessel["speed"] + np.random.uniform(-2, 2), 0, 30)), 1
            )

            frame_vessels.append(new_vessel)

        frames.append(frame_vessels)

    return frames


if __name__ == "__main__":
    # Test data generation
    vessels = generate_traffic_data(10)
    print(f"Generated {len(vessels)} vessels")
    for v in vessels[:3]:
        print(v)
