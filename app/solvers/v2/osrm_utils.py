import requests
import json
import time
import math
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

def get_manhattan_geometry(coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
    """
    Generates a grid-based Manhattan path between points.
    Creates 1-2 turns between each point to simulate street navigation.
    """
    full_path = []
    total_dist = 0
    
    for i in range(len(coordinates) - 1):
        p1 = coordinates[i]
        p2 = coordinates[i+1]
        
        # Manhattan path: [lat1, lng1] -> [lat1, lng2] -> [lat2, lng2]
        # We add a bit of "zig-zag" if they are far apart
        mid_lng = p2[1]
        mid_lat = p1[0]
        
        corner = (mid_lat, mid_lng)
        
        if i == 0:
            full_path.append(p1)
        full_path.append(corner)
        full_path.append(p2)
        
        # Distance calculation (L1 distance)
        dy = abs(p1[0] - p2[0]) * 111000
        dx = abs(p1[1] - p2[1]) * 111000 * math.cos(math.radians(p1[0]))
        total_dist += (dx + dy)
        
    return {
        "geometry": encode_polyline(full_path),
        "distance": total_dist,
        "duration": total_dist / 11.0 # ~40km/h
    }

def get_osrm_distance_matrix(coordinates: List[Tuple[float, float]]) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Returns (distance_matrix, duration_matrix) for the given coordinates.
    Tries OSRM first, falls back to Manhattan distance for speed.
    """
    coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])
    url = f"{OSRM_BASE_URL}/table/v1/driving/{coords_str}?annotations=distance,duration"
    headers = {"User-Agent": "QuantumLogisticsDemo/1.0"}
    
    try:
        # Short timeout for speed as requested
        response = requests.get(url, timeout=3, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "Ok":
            return data["distances"], data["durations"]
    except:
        pass

    # Manhattan Distance Fallback (Instant)
    n = len(coordinates)
    dist_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    dur_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j: continue
            dy = abs(coordinates[i][0] - coordinates[j][0]) * 111000
            dx = abs(coordinates[i][1] - coordinates[j][1]) * 111000 * math.cos(math.radians(coordinates[i][0]))
            dist = dx + dy
            dist_matrix[i][j] = dist
            dur_matrix[i][j] = dist / 11.0
    return dist_matrix, dur_matrix

def get_osrm_route(coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
    """
    Fetches route geometry. Tries OSRM, falls back to In-House Manhattan Grid.
    """
    coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coords_str}?overview=full&geometries=polyline"
    headers = {"User-Agent": "QuantumLogisticsDemo/1.0"}
    
    try:
        # Try OSRM with short timeout
        response = requests.get(url, timeout=3, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "Ok":
            route = data["routes"][0]
            return {
                "geometry": route["geometry"],
                "distance": route["distance"],
                "duration": route["duration"]
            }
    except:
        pass

    # In-house Manhattan Grid Router (Instant & No API Call)
    return get_manhattan_geometry(coordinates)
