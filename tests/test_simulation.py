"""Tests for maritime traffic simulation."""

import pytest

from seamulator.data.sample_data import PORTS
from seamulator.simulation.route_calculator import RouteCalculator
from seamulator.simulation.simulation import MaritimeSimulation


class TestRouteCalculator:
    """Test route calculation using searoute."""

    @pytest.fixture
    def route_calc(self) -> RouteCalculator:
        """Create a route calculator for tests."""
        return RouteCalculator()

    def test_calculate_route_between_north_sea_ports(
        self, route_calc: RouteCalculator
    ) -> None:
        """Test calculating a route between two North Sea ports."""
        rotterdam = PORTS["Rotterdam"]
        hamburg = PORTS["Hamburg"]

        route = route_calc.calculate_route(rotterdam, hamburg)

        assert route is not None
        assert len(route) > 0

    def test_calculate_route_distance_between_ports(
        self, route_calc: RouteCalculator
    ) -> None:
        """Test calculating distance between two ports."""
        rotterdam = PORTS["Rotterdam"]
        hamburg = PORTS["Hamburg"]

        distance = route_calc.calculate_route_distance(rotterdam, hamburg)

        assert distance is not None
        assert 0 < distance < 1000

    def test_calculate_route_multiple_ports(self, route_calc: RouteCalculator) -> None:
        """Test calculating routes between multiple North Sea port pairs."""
        port_names = list(PORTS.keys())

        for i, start_name in enumerate(port_names[:5]):
            for j, end_name in enumerate(port_names[:5]):
                if i == j:
                    continue

                start = PORTS[start_name]
                end = PORTS[end_name]

                route = route_calc.calculate_route(start, end)
                distance = route_calc.calculate_route_distance(start, end)

                assert route is not None
                assert distance is not None
                assert distance > 0


class TestMaritimeSimulation:
    """Test maritime traffic simulation."""

    @pytest.fixture
    def simulation(self) -> MaritimeSimulation:
        """Create a simulation for tests."""
        return MaritimeSimulation(num_vessels=5)

    def test_initialization(self, simulation: MaritimeSimulation) -> None:
        """Test simulation initialization."""
        state = simulation.get_state()

        assert "vessels" in state
        assert "time" in state
        assert "is_running" in state
        assert "speed_factor" in state

        assert state["time"] == 0.0
        assert state["is_running"] is False
        assert state["speed_factor"] == 1.0

    def test_vessel_count(self, simulation: MaritimeSimulation) -> None:
        """Test that vessels are created."""
        count = simulation.get_vessel_count()
        assert count <= 5
        assert count > 0

    def test_vessel_structure(self, simulation: MaritimeSimulation) -> None:
        """Test that vessels have correct structure."""
        vessels = simulation.get_vessel_positions()

        assert len(vessels) > 0

        for vessel in vessels:
            assert "id" in vessel
            assert "name" in vessel
            assert "type" in vessel
            assert "lat" in vessel
            assert "lon" in vessel
            assert "speed" in vessel
            assert "size" in vessel
            assert "color" in vessel
            assert "port" in vessel
            assert "destination" in vessel

            assert 5 <= vessel["speed"] <= 15
            assert -90 <= vessel["lat"] <= 90
            assert -180 <= vessel["lon"] <= 180

    def test_start_pause(self, simulation: MaritimeSimulation) -> None:
        """Test start and pause functionality."""
        assert simulation.get_state()["is_running"] is False

        simulation.start()
        assert simulation.get_state()["is_running"] is True

        simulation.pause()
        assert simulation.get_state()["is_running"] is False

    def test_reset(self, simulation: MaritimeSimulation) -> None:
        """Test reset functionality."""
        simulation.start()
        simulation.step(time_delta=10.0)

        state_before = simulation.get_state()
        assert state_before["time"] > 0

        simulation.reset()

        state_after = simulation.get_state()
        assert state_after["time"] == 0.0
        assert state_after["is_running"] is False

    def test_speed_factor(self, simulation: MaritimeSimulation) -> None:
        """Test speed factor setting."""
        simulation.set_speed_factor(2.0)
        assert simulation.get_state()["speed_factor"] == 2.0

        simulation.set_speed_factor(0.5)
        assert simulation.get_state()["speed_factor"] == 0.5

        simulation.set_speed_factor(0.0)
        assert simulation.get_state()["speed_factor"] >= 0.1

        simulation.set_speed_factor(100.0)
        assert simulation.get_state()["speed_factor"] <= 10.0

    def test_step_while_paused(self, simulation: MaritimeSimulation) -> None:
        """Test that stepping while paused doesn't advance time."""
        initial_time = simulation.get_state()["time"]
        simulation.step(time_delta=1.0)
        assert simulation.get_state()["time"] == initial_time

    def test_step_while_running(self, simulation: MaritimeSimulation) -> None:
        """Test that stepping while running advances time."""
        simulation.start()
        initial_time = simulation.get_state()["time"]
        simulation.step(time_delta=1.0)
        assert simulation.get_state()["time"] > initial_time

    def test_step_vessel_movement(self) -> None:
        """Test that a vessel moves correctly after one step."""
        # Create simulation with no vessels
        simulation = MaritimeSimulation(num_vessels=0)
        simulation.start()

        # Add a preconfigured vessel from Rotterdam to Hamburg
        vessel_id = simulation.add_vessel(
            name="TestVessel",
            vessel_type="Cargo",
            current_port="Rotterdam",
            destination_port="Hamburg",
            speed=10.0,
            color="#FF0000",
            size=1.0,
        )

        # Get initial vessel state
        initial_vessel = simulation.get_vessel(vessel_id)

        # Verify vessel starts at Rotterdam (or near it)
        initial_pos = initial_vessel["current_position"]
        rotterdam_pos = PORTS["Rotterdam"]
        assert abs(initial_pos[0] - rotterdam_pos[0]) < 0.1
        assert abs(initial_pos[1] - rotterdam_pos[1]) < 0.1

        # Verify vessel has a route with at least 2 waypoints
        assert len(initial_vessel["route"]) >= 2

        # Verify destination port is Hamburg
        assert initial_vessel["destination_port"] == "Hamburg"

        # Store initial position and heading
        initial_lat = initial_vessel["current_position"][0]
        initial_lon = initial_vessel["current_position"][1]
        initial_heading = initial_vessel["heading"]

        # Take one step
        simulation.step(time_delta=1.0)

        # Get updated vessel state
        updated_vessel = simulation.get_vessel(vessel_id)

        # Verify vessel has moved (position should be different)
        updated_lat = updated_vessel["current_position"][0]
        updated_lon = updated_vessel["current_position"][1]

        # The vessel should have moved from its initial position
        assert (updated_lat, updated_lon) != (initial_lat, initial_lon)

        # Verify heading has been updated and is valid (0-360 degrees)
        updated_heading = updated_vessel["heading"]
        assert 0 <= updated_heading <= 360
        # Verify heading has changed (vessel is facing a different direction)
        # Allow for floating point precision and wrap-around at 360
        assert (
            abs(updated_heading - initial_heading) > 0.01
            or abs((updated_heading - initial_heading + 360) % 360) > 0.01
        )

    def test_vessels_stay_in_north_sea(self, simulation: MaritimeSimulation) -> None:
        """Test that vessels stay within North Sea bounds."""
        simulation.start()
        for _ in range(10):
            simulation.step(time_delta=1.0)

        vessels = simulation.get_vessel_positions()

        assert len(vessels) > 0

        for vessel in vessels:
            assert 48 <= vessel["lat"] <= 61
            assert -5 <= vessel["lon"] <= 15
