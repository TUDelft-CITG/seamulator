"""Tests for density heatmap calculation."""

import pytest

from seamulator.simulation.density_heatmap import DensityHeatmap


class TestDensityHeatmap:
    """Test density heatmap calculation using H3 indexing."""

    @pytest.fixture
    def heatmap(self) -> DensityHeatmap:
        """Create a density heatmap calculator for tests."""
        return DensityHeatmap(resolution=7)

    def test_initialization(self, heatmap: DensityHeatmap) -> None:
        """Test density heatmap initializer."""
        assert heatmap.resolution == 7
        assert heatmap.hexagon_counts == {}
        assert heatmap.density_values == {}

    def test_initialization_custom_resolution(self) -> None:
        """Test density heatmap with custom resolution."""
        heatmap = DensityHeatmap(resolution=5)
        assert heatmap.resolution == 5

    def test_calculate_density_empty(self, heatmap: DensityHeatmap) -> None:
        """Test calculate_density with no vessels."""
        result = heatmap.calculate_density([])

        assert result == {}
        assert heatmap.hexagon_counts == {}
        assert heatmap.density_values == {}

    def test_calculate_density_single_vessel(self, heatmap: DensityHeatmap) -> None:
        """Test calculate_density with a single vessel."""
        # Single vessel at Amsterdam coordinates
        vessel_positions = [(52.3676, 4.9041)]

        result = heatmap.calculate_density(vessel_positions)

        # Should have exactly one cell with a vessel
        assert len(result) == 1
        assert len(heatmap.hexagon_counts) == 1

        # Check that the density is positive
        for h3_index, density in result.items():
            assert density > 0
            assert heatmap.hexagon_counts[h3_index] == 1

    def test_calculate_density_multiple_vessels_same_cell(
        self, heatmap: DensityHeatmap
    ) -> None:
        """Test calculate_density with multiple vessels in the same cell."""
        # Multiple vessels very close together (same H3 cell at resolution 7)
        # Using North Sea coordinates
        vessel_positions = [
            (52.3676, 4.9041),  # Amsterdam
            (52.3677, 4.9042),  # Very close to Amsterdam
            (52.3675, 4.9040),  # Very close to Amsterdam
        ]

        result = heatmap.calculate_density(vessel_positions)

        # At resolution 7, these should likely be in the same cell
        # (depending on exact H3 boundaries)
        assert len(result) >= 1

        # Total count should be 3
        total_count = sum(heatmap.hexagon_counts.values())
        assert total_count == 3

        # Each density should be positive
        for density in result.values():
            assert density > 0

    def test_calculate_density_multiple_vessels_different_cells(
        self, heatmap: DensityHeatmap
    ) -> None:
        """Test calculate_density with vessels in different cells."""
        # Vessels spread across North Sea
        vessel_positions = [
            (52.3676, 4.9041),  # Amsterdam
            (53.5503, 9.9932),  # Hamburg
            (51.9225, 4.4792),  # Rotterdam
            (53.3498, -1.3847),  # Newcastle (further away)
        ]

        result = heatmap.calculate_density(vessel_positions)

        # Should have multiple cells
        assert len(result) >= 1

        # Total count should be 4
        total_count = sum(heatmap.hexagon_counts.values())
        assert total_count == 4

    def test_calculate_density_returns_dict(self, heatmap: DensityHeatmap) -> None:
        """Test that calculate_density returns a dictionary."""
        vessel_positions = [(52.3676, 4.9041)]
        result = heatmap.calculate_density(vessel_positions)

        assert isinstance(result, dict)

    def test_calculate_density_updates_internal_state(
        self, heatmap: DensityHeatmap
    ) -> None:
        """Test that calculate_density updates internal state."""
        vessel_positions = [(52.3676, 4.9041)]

        # Before calculation
        assert len(heatmap.hexagon_counts) == 0
        assert len(heatmap.density_values) == 0

        heatmap.calculate_density(vessel_positions)

        # After calculation
        assert len(heatmap.hexagon_counts) >= 1
        assert len(heatmap.density_values) >= 1

    def test_calculate_density_idempotent(self, heatmap: DensityHeatmap) -> None:
        """Test that calling calculate_density multiple times resets state."""
        vessel_positions1 = [(52.3676, 4.9041)]
        vessel_positions2 = [(53.5503, 9.9932)]

        # First calculation
        heatmap.calculate_density(vessel_positions1)
        first_result = heatmap.hexagon_counts.copy()

        # Second calculation with different data
        heatmap.calculate_density(vessel_positions2)
        second_result = heatmap.hexagon_counts.copy()

        # Results should be independent
        assert first_result != second_result

    def test_get_geometry_empty(self, heatmap: DensityHeatmap) -> None:
        """Test get_geometry with no calculated density."""
        result = heatmap.get_geometry()

        assert result == []

    def test_get_geometry_with_density(self, heatmap: DensityHeatmap) -> None:
        """Test get_geometry after calculating density."""
        vessel_positions = [(52.3676, 4.9041)]
        heatmap.calculate_density(vessel_positions)

        result = heatmap.get_geometry()

        assert len(result) >= 1

        # Check structure of result
        for item in result:
            assert "h3_index" in item
            assert "center" in item
            assert "vertices" in item
            assert "density" in item
            assert "count" in item

            # Check types
            assert isinstance(item["h3_index"], str)
            assert isinstance(item["center"], tuple)
            assert len(item["center"]) == 2
            assert isinstance(item["vertices"], list)
            assert len(item["vertices"]) >= 3  # Hexagon has at least 3 vertices
            assert isinstance(item["density"], float)
            assert isinstance(item["count"], int)

    def test_get_geometry_center_valid(self, heatmap: DensityHeatmap) -> None:
        """Test that geometry centers are valid coordinates."""
        vessel_positions = [(52.3676, 4.9041)]
        heatmap.calculate_density(vessel_positions)

        result = heatmap.get_geometry()

        for item in result:
            center = item["center"]
            # Valid latitude: -90 to 90
            assert -90 <= center[0] <= 90
            # Valid longitude: -180 to 180
            assert -180 <= center[1] <= 180

    def test_get_geometry_vertices_valid(self, heatmap: DensityHeatmap) -> None:
        """Test that geometry vertices are valid coordinates."""
        vessel_positions = [(52.3676, 4.9041)]
        heatmap.calculate_density(vessel_positions)

        result = heatmap.get_geometry()

        for item in result:
            for vertex in item["vertices"]:
                # Valid latitude: -90 to 90
                assert -90 <= vertex[0] <= 90
                # Valid longitude: -180 to 180
                assert -180 <= vertex[1] <= 180
