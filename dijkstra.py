
import heapq
from typing import Dict, List, Optional, Set, Tuple
from graph import BlockedZone, Graph, Zone


class Pathfinder:

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_multiple_paths(
        self, start_zone: Zone, end_zone: Zone, max_paths: int = 3
    ) -> List[List[str]]:
        first_path = self._dijkstra(start_zone.name,
                                    end_zone.name, excluded_edges=set())
        if not first_path:
            return []

        paths: List[List[str]] = [first_path]

        for i in range(len(first_path) - 1):
            if len(paths) >= max_paths:
                break

            excluded = {(first_path[i], first_path[i + 1])}
            alt_path = self._dijkstra(start_zone.name,
                                      end_zone.name, excluded_edges=excluded)

            if alt_path and alt_path not in paths:
                paths.append(alt_path)

        return paths

    def _dijkstra(
        self, start_name: str, end_name: str,
        excluded_edges: Set[Tuple[str, str]]
    ) -> Optional[List[str]]:
        distances: Dict[str, float] = {name: float("inf") for
                                       name in self.graph.zones}
        previous: Dict[str, Optional[str]] = {name: None for name
                                              in self.graph.zones}

        distances[start_name] = 0.0
        pq: List[Tuple[float, str]] = [(0.0, start_name)]

        while pq:
            current_dist, current_name = heapq.heappop(pq)

            if current_dist > distances[current_name]:
                continue

            if current_name == end_name:
                break

            current_zone = self.graph.zones[current_name]

            for neighbor_zone, conn in self.graph.get_neighbors(current_zone):
                neighbor_name = neighbor_zone.name

                if (current_name, neighbor_name) in excluded_edges:
                    continue

                if isinstance(neighbor_zone, BlockedZone)\
                        or getattr(neighbor_zone, 'color', '') == 'black':
                    continue

                step_cost = float(neighbor_zone.get_travel_cost())
                new_dist = current_dist + step_cost

                if new_dist < distances.get(neighbor_name, float("inf")):
                    distances[neighbor_name] = new_dist
                    previous[neighbor_name] = current_name
                    heapq.heappush(pq, (new_dist, neighbor_name))

        if end_name not in previous or (previous[end_name]
                                        is None and start_name != end_name):
            return None

        path: List[str] = []
        curr: Optional[str] = end_name
        while curr is not None:
            path.append(curr)
            curr = previous[curr]

        path.reverse()
        return path
    def assign_paths_to_drones(
        self, paths: List[List[str]], nb_drones: int
                                ) -> Dict[int, List[str]]:
        drone_assignments: Dict[int, List[str]] = {}
        if not paths:
                return drone_assignments
        turns_per_path = []
        for p in paths:
            turns = 0
            for zone_name in p[1:]:  
                zone_obj = self.graph.zones[zone_name]
                turns += zone_obj.get_travel_cost()
            turns_per_path.append(turns)

        min_turns = min(turns_per_path)
        best_paths = []
        for idx, turns in enumerate(turns_per_path):
            if turns == min_turns:
             best_paths.append(paths[idx])

        for drone_id in range(1, nb_drones + 1):
            chosen_path = best_paths[(drone_id - 1) % len(best_paths)]
            drone_assignments[drone_id] = chosen_path

        return drone_assignments                
