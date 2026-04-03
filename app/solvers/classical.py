import math
import time
from typing import List, Dict, Any

try:
    from ortools.constraint_solver import pywrapcp
    from ortools.constraint_solver import routing_enums_pb2
    ORTOOLS_AVAILABLE = True
except (ImportError, FileNotFoundError, OSError):
    ORTOOLS_AVAILABLE = False

def compute_euclidean_distance_matrix(locations: List[tuple]) -> List[List[int]]:
    matrix = []
    for from_node in locations:
        row = []
        for to_node in locations:
            dist = math.hypot(from_node[0] - to_node[0], from_node[1] - to_node[1])
            row.append(int(dist * 10000))
        matrix.append(row)
    return matrix

def solve_classical(
    coordinates: List[Dict[str, Any]],
    depot_index: int,
    no_of_trucks: int
) -> Dict[str, Any]:
    start_time = time.time()
    
    locations = [(round(c['lat'], 6), round(c['lng'], 6)) for c in coordinates]
    
    if ORTOOLS_AVAILABLE:
        data = {}
        data['distance_matrix'] = compute_euclidean_distance_matrix(locations)
        data['num_vehicles'] = no_of_trucks
        data['depot'] = depot_index

        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']), data['num_vehicles'], data['depot']
        )
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            30000000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        solution = routing.SolveWithParameters(search_parameters)
        
        end_time = time.time()

        if not solution:
            raise Exception("No classical solution found!")

        routes = []
        total_distance = 0
        max_route_distance = 0
        
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            path = []
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                path.append(coordinates[node_index]['id'])
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            node_index = manager.IndexToNode(index)
            path.append(coordinates[node_index]['id'])
            
            routes.append({
                "vehicle_id": vehicle_id + 1,
                "path": path,
                "distance": route_distance / 10000.0
            })
            
            max_route_distance = max(route_distance, max_route_distance)
            total_distance += route_distance

        return {
            "routes": routes,
            "noOfSteps": 1,
            "internalLogicDetails": {
                "algorithm": "classical (OR-Tools)",
                "execution_time_sec": round(end_time - start_time, 4),
                "total_distance": round(total_distance / 10000.0, 4),
                "objective_value": round(solution.ObjectiveValue() / 10000.0, 4),
                "solver_status": routing.status()
            }
        }

    else:
        # Fallback Greedy Implementation when OR-Tools is missing
        # Split nodes across vehicles evenly and do Greedy TSP
        import networkx as nx
        
        G = nx.Graph()
        for i in range(len(locations)):
            G.add_node(i, pos=locations[i], id=coordinates[i]['id'])
            for j in range(i + 1, len(locations)):
                dist = math.hypot(locations[i][0] - locations[j][0], locations[i][1] - locations[j][1])
                G.add_edge(i, j, weight=dist)
                
        all_indices = set(range(len(locations)))
        client_indices = list(all_indices - {depot_index})
        
        routes = []
        total_distance = 0.0
        
        # simple round-robin assignment of nodes to trucks
        cluster_map = {i: [] for i in range(no_of_trucks)}
        for idx, client_idx in enumerate(client_indices):
            cluster_map[idx % no_of_trucks].append(client_idx)
            
        for truck_idx, nodes_in_cluster in cluster_map.items():
            if not nodes_in_cluster:
                # empty truck route
                routes.append({
                    "vehicle_id": truck_idx + 1,
                    "path": [coordinates[depot_index]['id'], coordinates[depot_index]['id']],
                    "distance": 0.0
                })
                continue
            
            path_nodes = [depot_index]
            unvisited = nodes_in_cluster.copy()
            current = depot_index
            route_dist = 0.0
            
            while unvisited:
                nearest = min(unvisited, key=lambda n: G[current][n]['weight'])
                route_dist += G[current][nearest]['weight']
                current = nearest
                path_nodes.append(current)
                unvisited.remove(current)
                
            # return to depot
            route_dist += G[current][depot_index]['weight']
            path_nodes.append(depot_index)
            
            real_path_ids = [coordinates[n]['id'] for n in path_nodes]
            
            routes.append({
                "vehicle_id": truck_idx + 1,
                "path": real_path_ids,
                "distance": round(route_dist, 4)
            })
            total_distance += route_dist

        end_time = time.time()
        
        return {
            "routes": routes,
            "noOfSteps": 1,
            "internalLogicDetails": {
                "algorithm": "classical (Greedy Fallback)",
                "execution_time_sec": round(end_time - start_time, 4),
                "total_distance": round(total_distance, 4),
                "solver_status": "Fallback"
            }
        }
