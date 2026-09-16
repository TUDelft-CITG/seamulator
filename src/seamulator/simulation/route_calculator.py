"""Route calculation using searoute library for maritime paths."""

import math

import searoute as sr


class RouteCalculator:
    """Calculate maritime routes between ports using searoute.

    This class wraps the searoute library to provide pathfinding
    capabilities between maritime ports.
    """

    def calculate_route(
        self, start_port: tuple[float, float], end_port: tuple[float, float]
    ) -> list[tuple[float, float]]:
        """Calculate the shortest route between two ports.

        Args:
            start_port: Tuple of (latitude, longitude) for the starting port.
            end_port: Tuple of (latitude, longitude) for the destination port.

        Returns:
            List of (latitude, longitude) tuples representing the path.
        """
        # searoute expects (lon, lat) tuples
        origin = (start_port[1], start_port[0])
        destination = (end_port[1], end_port[0])

        # Get route as GeoJSON Feature
        route_feature = sr.searoute(origin, destination)

        # Extract coordinates from the LineString geometry
        # Coordinates are in [lon, lat] format
        coords = route_feature["geometry"]["coordinates"]

        # Convert from [lon, lat] to (lat, lon) tuples
        return [(float(p[1]), float(p[0])) for p in coords]

    def calculate_route_distance(
        self, start_port: tuple[float, float], end_port: tuple[float, float]
    ) -> float:
        """Calculate the distance of the shortest route between two ports in NM.

        Args:
            start_port: Tuple of (latitude, longitude) for the starting port.
            end_port: Tuple of (latitude, longitude) for the destination port.

        Returns:
            Distance in nautical miles.
        """
        origin = (start_port[1], start_port[0])
        destination = (end_port[1], end_port[0])

        route_feature = sr.searoute(origin, destination)
        coords = route_feature["geometry"]["coordinates"]

        # Calculate distance using haversine formula
        total_distance_nm = 0.0
        prev_point = coords[0]

        for point in coords[1:]:
            prev_lon, prev_lat = prev_point
            curr_lon, curr_lat = point
            segment_distance = self._haversine_distance(
                prev_lat, prev_lon, curr_lat, curr_lon
            )
            total_distance_nm += segment_distance
            prev_point = point

        return round(total_distance_nm, 2)

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate the great-circle distance between two points in nautical miles.

        Args:
            lat1: Latitude of point 1 in degrees.
            lon1: Longitude of point 1 in degrees.
            lat2: Latitude of point 2 in degrees.
            lon2: Longitude of point 2 in degrees.

        Returns:
            Distance in nautical miles.
        """
        earth_radius_nm = 3440.069

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = earth_radius_nm * c

        return distance
