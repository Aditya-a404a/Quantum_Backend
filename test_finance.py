import requests
import json

def test_finance_solve():
    url = "http://localhost:8000/api/v1/finance/solve"
    payload = {
        "numAssets": 5,
        "riskTolerance": 0.5,
        "costFactor": 0.2
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Successfully received data!")
            print(f"Classical Return: {data['classical']['expectedReturn']}%")
            print(f"Quantum Return: {data['quantum']['expectedReturn']}%")
            print(f"Frontier Points: {len(data['frontierData'])}")
            print(f"Allocations (Classical): {len(data['classical']['allocation'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_finance_solve()
