"""Discrete event simulation for maritime traffic."""

from __future__ import annotations

from typing import Any

import numpy as np
from haversine import Unit, haversine
from typing_extensions import TypedDict

from seamulator.data.sample_data import PORTS
from seamulator.simulation.route_calculator import RouteCalculator


class VesselState(TypedDict):
    """Represents the state of a single vessel in the simulation.

    Attributes:
        id: Unique identifier for the vessel.
        name: Name of the vessel.
        vessel_type: Type/category of the vessel (e.g., Cargo, Tanker).
        current_port: Name of the current port the vessel is at or came from.
        destination_port: Name of the destination port the vessel is heading to.
        speed: Speed of the vessel in knots.
        route: List of (lat, lon) waypoints for vessel's path.
        current_position: Current (latitude, longitude) position.
        route_index: Current index in the route list.
        color: Color associated with the vessel type for visualization.
        size: Size of the vessel for visualization scaling.
    """

    id: int
    name: str
    vessel_type: str
    current_port: str
    destination_port: str
    speed: float
    route: list[tuple[float, float]]
    current_position: tuple[float, float]
    route_index: int
    color: str
    size: float


class SimulationState(TypedDict):
    """Represents the overall simulation state.

    Attributes:
        vessels: Dictionary of all vessels indexed by vessel ID.
        time: Current simulation time in hours.
        is_running: Whether the simulation is currently running or paused.
        speed_factor: Simulation speed multiplier (1.0 = normal speed).
    """

    vessels: dict[int, VesselState]
    time: float
    is_running: bool
    speed_factor: float


class MaritimeSimulation:
    """Discrete event-time simulation for maritime traffic.

    The simulation manages multiple vessels moving between ports
    along pre-calculated routes using maritime routing data.
    """

    def __init__(self, num_vessels: int = 10) -> None:
        """Initialize the maritime simulation.

        Args:
            num_vessels: Number of vessels to create in the simulation.
        """
        self.route_calculator = RouteCalculator()
        self.num_vessels = num_vessels
        self.state: SimulationState = {
            "vessels": {},
            "time": 0.0,
            "is_running": False,
            "speed_factor": 1.0,
        }
        self._next_vessel_id = 1
        self._initialize_vessels()

    def _initialize_vessels(self) -> None:
        """Create initial vessels at random ports with random destinations."""
        port_names = list(PORTS.keys())

        for _ in range(self.num_vessels):
            # Random start port
            start_port = np.random.choice(port_names)
            start_coords = PORTS[start_port]

            # Random destination port (different from start)
            dest_port = np.random.choice([p for p in port_names if p != start_port])
            dest_coords = PORTS[dest_port]

            # Calculate route
            route = self.route_calculator.calculate_route(start_coords, dest_coords)

            # Random speed between 5 and 15 knots
            speed = round(float(np.random.uniform(5, 15)), 1)

            # Get vessel type info
            from seamulator.data.sample_data import (
                VESSEL_TYPES,
                generate_vessel_name,
            )

            vessel_type = np.random.choice(list(VESSEL_TYPES.keys()))
            vessel_info = VESSEL_TYPES[vessel_type]

            vessel: VesselState = {
                "id": self._next_vessel_id,
                "name": generate_vessel_name(vessel_type, self._next_vessel_id),
                "vessel_type": vessel_type,
                "current_port": start_port,
                "destination_port": dest_port,
                "speed": speed,
                "route": route,
                "current_position": route[0],
                "route_index": 0,
                "color": vessel_info["color"],
                "size": vessel_info["size"],
            }

            self.state["vessels"][self._next_vessel_id] = vessel
            self._next_vessel_id += 1

    def _get_vessel_from_dict(self, vessel_dict: dict[str, Any]) -> VesselState:
        """Convert a dictionary to a VesselState typed dict."""
        return VesselState(**vessel_dict)

    def step(self, time_delta: float = 1.0) -> None:
        """Advance the simulation by one time step.

        Args:
            time_delta: Time to advance in hours.
        """
        if not self.state["is_running"]:
            return

        # Apply speed factor
        effective_time_delta = time_delta * self.state["speed_factor"]
        self.state["time"] += effective_time_delta

        vessels_to_update = {}

        for vessel_id, vessel in self.state["vessels"].items():
            vessel = self._get_vessel_from_dict(vessel)

            # If vessel has no route or has reached the end, assign new destination
            if vessel["route_index"] >= len(vessel["route"]) - 1:
                # Vessel has arrived at destination
                new_destination = self._assign_new_destination(vessel)
                if new_destination:
                    vessels_to_update[vessel_id] = new_destination
                continue

            # Calculate distance to next waypoint in nautical miles
            current_pos = vessel["current_position"]
            next_pos = vessel["route"][vessel["route_index"] + 1]

            # Use haversine library to calculate distance in nautical miles
            distance_nm = haversine(current_pos, next_pos, unit=Unit.NAUTICAL_MILES)

            # Time to reach next waypoint in hours
            # time = distance / speed
            time_to_next = distance_nm / vessel["speed"]

            # If we can reach the next waypoint within this time step
            if effective_time_delta >= time_to_next:
                # Move to next waypoint
                remaining_time = effective_time_delta - time_to_next
                vessel["current_position"] = next_pos
                vessel["route_index"] += 1

                # Recursively handle remaining time from the next position
                self._step_vessel(vessel, remaining_time)

                vessels_to_update[vessel_id] = vessel
            else:
                # Move partway towards next waypoint
                fraction = effective_time_delta / time_to_next
                new_lat = current_pos[0] + fraction * (next_pos[0] - current_pos[0])
                new_lon = current_pos[1] + fraction * (next_pos[1] - current_pos[1])

                vessel["current_position"] = (
                    round(new_lat, 6),
                    round(new_lon, 6),
                )
                vessels_to_update[vessel_id] = vessel

        # Update all vessels
        for vessel_id, vessel in vessels_to_update.items():
            self.state["vessels"][vessel_id] = vessel

    def _step_vessel(self, vessel: VesselState, time_delta: float) -> None:
        """Helper to step a single vessel (for recursive calls).

        Args:
            vessel: The vessel to update.
            time_delta: Remaining time to advance.
        """
        if vessel["route_index"] >= len(vessel["route"]) - 1:
            return

        current_pos = vessel["current_position"]
        next_pos = vessel["route"][vessel["route_index"] + 1]

        distance_nm = haversine(current_pos, next_pos, unit=Unit.NAUTICAL_MILES)
        time_to_next = distance_nm / vessel["speed"]

        if time_delta >= time_to_next:
            remaining_time = time_delta - time_to_next
            vessel["current_position"] = next_pos
            vessel["route_index"] += 1
            self._step_vessel(vessel, remaining_time)
        else:
            fraction = time_delta / time_to_next
            new_lat = current_pos[0] + fraction * (next_pos[0] - current_pos[0])
            new_lon = current_pos[1] + fraction * (next_pos[1] - current_pos[1])
            vessel["current_position"] = (round(new_lat, 6), round(new_lon, 6))

    def _assign_new_destination(self, vessel: VesselState) -> VesselState:
        """Assign a new random destination to a vessel.

        Args:
            vessel: The vessel that needs a new destination.

        Returns:
            Updated vessel with new route.
        """
        port_names = list(PORTS.keys())

        # Choose a different destination port
        current_port = vessel["destination_port"]
        possible_ports = [p for p in port_names if p != current_port]

        new_dest = np.random.choice(possible_ports)
        new_dest_coords = PORTS[new_dest]

        # Calculate new route from current position
        current_coords = vessel["current_position"]
        route = self.route_calculator.calculate_route(current_coords, new_dest_coords)

        # Update vessel
        vessel["current_port"] = vessel["destination_port"]
        vessel["destination_port"] = new_dest
        vessel["route"] = route
        vessel["current_position"] = route[0]
        vessel["route_index"] = 0

        return vessel

    def get_vessel_positions(self) -> list[dict[str, Any]]:
        """Get current positions of all vessels for visualization.

        Returns:
            List of dictionaries with vessel position data.
        """
        result = []
        for vessel_id, vessel in self.state["vessels"].items():
            vessel = self._get_vessel_from_dict(vessel)
            result.append(
                {
                    "id": vessel_id,
                    "name": vessel["name"],
                    "type": vessel["vessel_type"],
                    "lat": vessel["current_position"][0],
                    "lon": vessel["current_position"][1],
                    "speed": vessel["speed"],
                    "heading": 0,  # Would need to calculate based on route
                    "size": vessel["size"],
                    "color": vessel["color"],
                    "port": vessel["current_port"],
                    "destination": vessel["destination_port"],
                    "mmsi": vessel_id * 1000 + vessel_id,
                }
            )
        return result

    def start(self) -> None:
        """Start the simulation."""
        self.state["is_running"] = True

    def pause(self) -> None:
        """Pause the simulation."""
        self.state["is_running"] = False

    def reset(self) -> None:
        """Reset the simulation to initial state."""
        self.state = {
            "vessels": {},
            "time": 0.0,
            "is_running": False,
            "speed_factor": 1.0,
        }
        self._next_vessel_id = 1
        self._initialize_vessels()

    def set_speed_factor(self, factor: float) -> None:
        """Set the simulation speed multiplier.

        Args:
            factor: Speed multiplier (1.0 = normal speed).
        """
        self.state["speed_factor"] = max(0.1, min(factor, 10.0))

    def get_state(self) -> SimulationState:
        """Get the current simulation state.

        Returns:
            Current simulation state.
        """
        return self.state

    def get_vessel_count(self) -> int:
        """Get the number of vessels in the simulation.

        Returns:
            Number of vessels.
        """
        return len(self.state["vessels"])
