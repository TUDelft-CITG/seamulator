"""Tests for maritime traffic visualization."""


from seamulator.data.sample_data import (
    PORTS,
    VESSEL_TYPES,
    generate_random_vessel,
    generate_traffic_data,
)
from seamulator.visualization.components.controls import get_all_vessel_types
from seamulator.visualization.components.map import (
    add_vessels_to_map,
    create_base_map,
    create_traffic_map,
    get_vessel_marker_size,
)


class TestSampleData:
    """Test sample data generation."""

    def test_generate_random_vessel(self):
        """Test generating a single random vessel."""
        vessel = generate_random_vessel()

        assert isinstance(vessel, dict)
        assert "name" in vessel
        assert "type" in vessel
        assert "lat" in vessel
        assert "lon" in vessel
        assert "speed" in vessel
        assert "heading" in vessel
        assert "timestamp" in vessel
        assert "size" in vessel
        assert "color" in vessel
        assert "port" in vessel
        assert "mmsi" in vessel

        # Check value ranges
        assert -90 <= vessel["lat"] <= 90
        assert -180 <= vessel["lon"] <= 180
        assert 0 <= vessel["speed"] <= 25
        assert 0 <= vessel["heading"] < 360
        assert vessel["type"] in VESSEL_TYPES
        assert vessel["port"] in PORTS

    def test_generate_traffic_data(self):
        """Test generating multiple vessels."""
        vessels = generate_traffic_data(100)

        assert len(vessels) == 100
        assert all(isinstance(v, dict) for v in vessels)
        assert all(v["type"] in VESSEL_TYPES for v in vessels)

    def test_vessel_types_structure(self):
        """Test that vessel types have required attributes."""
        for vtype, attrs in VESSEL_TYPES.items():
            assert "size" in attrs
            assert "color" in attrs
            assert "icon" in attrs

    def test_ports_structure(self):
        """Test that ports have valid coordinates."""
        for port_name, (lat, lon) in PORTS.items():
            assert isinstance(port_name, str)
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180


class TestMapComponents:
    """Test map visualization components."""

    def test_create_base_map(self):
        """Test creating a base map figure."""
        fig = create_base_map()

        assert fig is not None
        assert hasattr(fig, "layout")
        assert "map" in fig.layout
        assert fig.layout.map.style == "open-street-map"
        # Center is a Center object in plotly 7
        assert fig.layout.map.center.lat == 20
        assert fig.layout.map.center.lon == 0
        assert fig.layout.map.zoom == 1

    def test_get_vessel_marker_size(self):
        """Test marker size calculation."""
        # Boundary cases
        assert get_vessel_marker_size(10) == 5  # Minimum
        assert get_vessel_marker_size(300) == 25  # Maximum

        # Middle value
        size_150 = get_vessel_marker_size(150)
        assert 5 <= size_150 <= 25

        # Linear scaling check
        size_55 = get_vessel_marker_size(55)
        expected_55 = (55 - 10) * 20 / 290 + 5
        assert abs(size_55 - expected_55) < 0.001

    def test_add_vessels_to_map(self):
        """Test adding vessels to a map."""
        fig = create_base_map()
        vessels = generate_traffic_data(10)

        fig = add_vessels_to_map(fig, vessels)

        assert fig is not None
        assert len(fig.data) == len(set(v["type"] for v in vessels))

    def test_create_traffic_map(self):
        """Test creating a complete traffic map."""
        vessels = generate_traffic_data(20)
        fig = create_traffic_map(vessels)

        assert fig is not None
        assert "Maritime Traffic Visualization" in fig.layout.title.text


class TestControls:
    """Test control components."""

    def test_get_all_vessel_types(self):
        """Test getting all vessel types."""
        types = get_all_vessel_types()

        assert isinstance(types, list)
        assert len(types) > 0
        assert all(isinstance(t, str) for t in types)
        assert set(types) == set(VESSEL_TYPES.keys())
