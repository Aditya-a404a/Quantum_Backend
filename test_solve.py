import requests
import json

def test_v2_solve():
    url = "http://localhost:8000/api/v2/logistics/solve"
    payload = {
        "depot": {"id": "depot", "lat": 40.7128, "lng": -74.0060},
        "coordinates": [
            {"id": "c1", "lat": 40.7138, "lng": -74.0070},
            {"id": "c2", "lat": 40.7148, "lng": -74.0080},
            {"id": "c3", "lat": 40.7158, "lng": -74.0090}
        ],
        "noOfTrucks": 2,
        "algorithm": "hybrid"
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response Keys:", data.keys())
            if "classical" in data:
                print("Classical Routes Count:", len(data["classical"]["routes"]))
                print("Classical Distance:", data["classical"]["total_distance"])
            if "quantum" in data:
                print("Quantum Routes Count:", len(data["quantum"]["routes"]))
                print("Quantum Distance:", data["quantum"]["total_distance"])
            
            # Check for geometry
            if data["classical"]["routes"] and data["classical"]["routes"][0]["geometry"]:
                print("Geometry Sample:", data["classical"]["routes"][0]["geometry"][:50] + "...")
            else:
                print("WARNING: Classical Route 0 has NO geometry!")
                
        else:
            print("Error Response:", response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_v2_solve()
