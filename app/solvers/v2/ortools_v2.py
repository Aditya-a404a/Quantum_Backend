import time
from typing import List, Dict, Any, Tuple
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from .osrm_utils import get_osrm_distance_matrix, get_osrm_route

def solve_vrp_ortools_v2(
    depot: Dict[str, Any],
    clients: List[Dict[str, Any]],
    num_vehicles: int
) -> Dict[str, Any]:
    """
    Solves VRP V2 using Google OR-Tools and real-world OSRM distances.
    """
    start_time = time.time()
    
    # 1. Coordinate Aggregation (Depot is index 0)
    all_points = [depot] + clients
    point_coords = [(p['lat'], p['lng']) for p in all_points]
    point_ids = [p['id'] for p in all_points]
    
    # 2. Get Real-World Matrices
    dist_matrix, dur_matrix = get_osrm_distance_matrix(point_coords)
    
    # 3. OR-Tools Setup
    manager = pywrapcp.RoutingIndexManager(len(point_coords), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(dist_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 4. Greedy Strategy & Constraints
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # "greedy strat" -> PATH_CHEAPEST_ARC for initial solution
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    
    # Balance routes
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        500000,  # 500km max distance
        True,
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # 5. Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        raise Exception("OR-Tools failed to find a valid route.")

    # 6. Post-Process Routes (Parallelized for Speed)
    from concurrent.futures import ThreadPoolExecutor
    
    routes_to_fetch = []
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        sequence_indices = []
        while not routing.IsEnd(index):
            sequence_indices.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        sequence_indices.append(manager.IndexToNode(index))
        
        if len(sequence_indices) > 2:
            route_coords = [point_coords[idx] for idx in sequence_indices]
            routes_to_fetch.append((vehicle_id, [point_ids[idx] for idx in sequence_indices], route_coords))
        else:
            routes_to_fetch.append((vehicle_id, [point_ids[0], point_ids[0]], None))

    def fetch_route_data(item):
        v_id, seq, coords = item
        if coords is None:
            return v_id, {"sequence": seq, "total_distance": 0, "total_duration": 0, "geometry": None}
        try:
            r_data = get_osrm_route(coords)
            return v_id, {
                "sequence": seq,
                "total_distance": r_data["distance"] / 1000.0,
                "total_duration": r_data["duration"] / 60.0,
                "geometry": r_data["geometry"]
            }
        except:
            return v_id, {"sequence": seq, "total_distance": 0, "total_duration": 0, "geometry": None}

    with ThreadPoolExecutor(max_workers=min(2, num_vehicles)) as executor:
        results = list(executor.map(fetch_route_data, routes_to_fetch))

    final_routes = []
    total_dist_km = 0
    total_dur_min = 0

    for v_id, r_info in sorted(results, key=lambda x: x[0]):
        final_routes.append({"truck_id": v_id + 1, **r_info})
        total_dist_km += r_info["total_distance"]
        total_dur_min += r_info["total_duration"]

    return {
        "status": "success",
        "routes": final_routes,
        "total_distance": round(total_dist_km, 2),
        "total_duration": round(total_dur_min, 2),
        "computation_time": time.time() - start_time,
        "solver_metadata": {
            "engine": "OR-Tools V2 (Parallel OSRM)",
            "strategy": "Multi-threaded Geometry Fetching",
            "threads": min(5, num_vehicles)
        }
    }
