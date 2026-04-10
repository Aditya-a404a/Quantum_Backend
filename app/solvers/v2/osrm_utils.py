import requests
import json
from typing import List, Tuple, Dict, Any

OSRM_BASE_URL = "https://router.project-osrm.org"

def encode_polyline(coords: List[Tuple[float, float]], precision: int = 5) -> str:
    """
    Standard Google Polyline Encoding Algorithm.
    """
    def _encode_val(val):
        val = int(round(val * 10**precision))
        val = ~(val << 1) if val < 0 else val << 1
        res = ""
        while val >= 0x20:
            res += chr((0x20 | (val & 0x1f)) + 63)
            val >>= 5
        res += chr(val + 63)
        return res

    res = ""
    last_lat, last_lng = 0, 0
    for lat, lng in coords:
        res += _encode_val(lat - last_lat)
        res += _encode_val(lng - last_lng)
        last_lat, last_lng = lat, lng
    return res


def get_osrm_distance_matrix(coordinates: List[Tuple[float, float]]) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Returns (distance_matrix, duration_matrix) for the given coordinates (lat, lng).
    Coordinates should be a list of (lat, lng) tuples.
    """
    import math
    coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])
    url = f"{OSRM_BASE_URL}/table/v1/driving/{coords_str}?annotations=distance,duration"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != "Ok":
            raise Exception(f"OSRM Error: {data['code']}")
            
        distances = data["distances"] # in meters
        durations = data["durations"] # in seconds
        return distances, durations
    except Exception as e:
        print(f"OSRM Failure - falling back to Euclidean: {e}")
        # Build manual Euclidean matrix
        n = len(coordinates)
        dist_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        dur_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j: continue
                # Very rough lat/lng to meters (1 deg ~ 111km)
                dy = (coordinates[i][0] - coordinates[j][0]) * 111000
                dx = (coordinates[i][1] - coordinates[j][1]) * 111000 * math.cos(math.radians(coordinates[i][0]))
                dist = math.sqrt(dx**2 + dy**2)
                dist_matrix[i][j] = dist
                dur_matrix[i][j] = dist / 11.0 # ~40km/h
        return dist_matrix, dur_matrix

def get_osrm_route(coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
    """
    Fetches the actual geometry and stats for a sequence of coordinates.
    Returns a dict with 'geometry', 'distance', 'duration'.
    """
    import math
    coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coords_str}?overview=full&geometries=polyline"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data["code"] != "Ok":
            raise Exception(f"OSRM Error: {data['code']}")
            
        route = data["routes"][0]
        return {
            "geometry": route["geometry"], # encoded polyline
            "distance": route["distance"], # meters
            "duration": route["duration"]  # seconds
        }
    except Exception as e:
        print(f"OSRM Route Failure - falling back to straight line: {e}")
        # Manual distance
        total_dist = 0
        for i in range(len(coordinates)-1):
            p1 = coordinates[i]
            p2 = coordinates[i+1]
            dy = (p1[0] - p2[0]) * 111000
            dx = (p1[1] - p2[1]) * 111000 * math.cos(math.radians(p1[0]))
            total_dist += math.sqrt(dx**2 + dy**2)
        
        # Simple polyline encoding for a straight line sequence
        return {
            "geometry": encode_polyline(coordinates),
            "distance": total_dist,
            "duration": total_dist / 11.0
        }
