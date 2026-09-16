"""Density heatmap calculation using H3 spatial indexing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import h3
import shapely

if TYPE_CHECKING:
    from geopandas import GeoDataFrame


class DensityHeatmap:
    """Calculate vessel density heatmap using H3 spatial indexing.

    This class uses Uber's H3 library to create hexagonal grids for
    aggregating vessel positions and calculating density values.
    """

    def __init__(self, resolution: int = 7) -> None:
        """Initialize the density heatmap calculator.

        Args:
            resolution: H3 resolution level (0-15). Higher values create finer grids.
                       Resolution 7 provides approximately 10km hexagons
                       at mid-latitudes.
        """
        self.resolution = resolution
        self.hexagon_counts: dict[str, int] = {}
        self.density_values: dict[str, float] = {}

    def calculate_density(
        self, vessel_positions: list[tuple[float, float]]
    ) -> dict[str, float]:
        """Calculate the density value for each H3 cell by aggregating vessel counts.

        Args:
            vessel_positions: List of (latitude, longitude) tuples for vessel positions.

        Returns:
            Dictionary mapping H3 cell index strings to density values
            (vessels per cell normalized by cell area).
        """
        # Reset counts for new calculation
        self.hexagon_counts = {}
        self.density_values = {}

        # Count vessels in each hexagon
        for lat, lon in vessel_positions:
            # Convert lat/lon to H3 index using h3 v4 API
            h3_index = h3.latlng_to_cell(lat, lon, self.resolution)
            self.hexagon_counts[h3_index] = self.hexagon_counts.get(h3_index, 0) + 1

        # Calculate density for each cell
        # Density = count / cell_area (in square km)
        # In h3 v4, cell_area takes a resolution parameter, not an index
        cell_area_km2 = h3.average_hexagon_area(self.resolution, "km^2")

        for h3_index, count in self.hexagon_counts.items():
            # Use average area for this resolution
            if cell_area_km2 > 0:
                self.density_values[h3_index] = count / cell_area_km2
            else:
                self.density_values[h3_index] = float(count)

        return self.density_values

    def get_geometry(self) -> GeoDataFrame:
        """Get the geometry representation of the H3 grid as a GeoDataFrame.

        Returns:
            GeoDataFrame containing geometry information for each hexagon with:
            - h3_index: The H3 cell index
            - center_lat: Latitude of cell center
            - center_lon: Longitude of cell center
            - density: Density value for this cell (vessels per km²)
            - count: Number of vessels in this cell
            - geometry: Polygon geometry of the hexagon
        """
        features = []

        for h3_index, density in self.density_values.items():
            # Get cell center using h3 v4 API
            center_lat, center_lon = h3.cell_to_latlng(h3_index)

            # Get cell boundary vertices using h3 v4 API
            vertices = h3.cell_to_boundary(h3_index)

            # Create a shapely Polygon from the vertices
            polygon = shapely.Polygon(vertices)

            features.append(
                {
                    "h3_index": h3_index,
                    "center_lat": center_lat,
                    "center_lon": center_lon,
                    "density": density,
                    "count": self.hexagon_counts.get(h3_index, 0),
                    "geometry": polygon,
                }
            )

        # Create GeoDataFrame with EPSG:4326 (WGS84) CRS
        columns = [
            "h3_index",
            "center_lat",
            "center_lon",
            "density",
            "count",
            "geometry",
        ]
        if not features:
            gdf = gpd.GeoDataFrame(columns=columns, crs="EPSG:4326")
        else:
            gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")

        return gdf
