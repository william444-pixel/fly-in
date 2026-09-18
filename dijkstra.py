import heapq
from typing import Dict, List, Optional, Set, Tuple
from graph import BlockedZone, Graph, Zone


class Pathfinder:

    def __init__(self, graph: Graph) -> None:
        """Initialize the Pathfinder with a graph instance."""
        self.graph = graph

    def find_shortest_path(
        self, start_zone: Zone, end_zone: Zone
    ) -> Optional[List[str]]:
        """Find the shortest path between start_zone
          and end_zone using Dijkstra's algorithm.

        Returns a list of zone names representing the path, or None if no path
        exists.
        """
        # 1. Initialization
        distances: Dict[str, float] = {start_zone.name: 0.0}
        previous: Dict[str, Optional[str]] = {start_zone.name: None}
        pq: List[Tuple[float, str]] = [(0.0, start_zone.name)]

        # Track visited zones to avoid reprocessing nodes
        visited: Set[str] = set()

        # 2. Main Dijkstra Loop
        while pq:
            current_cost, current_name = heapq.heappop(pq)

            # Target reached: optimal path found
            if current_name == end_zone.name:
                break

            # Skip processing if node has already been visited
            if current_name in visited:
                continue

            # Mark current zone as visited
            visited.add(current_name)

            # Explore all connections/neighbors of current_name
            for neighbor_zone, connection in self.graph.get_neighbors(
                self.graph.zones[current_name]
            ):
                neighbor_name = neighbor_zone.name

                # Skip neighbors that are already fully processed
                if neighbor_name in visited:
                    continue

                # Ignore blocked zones completely
                if isinstance(neighbor_zone, BlockedZone):
                    continue

                # Calculate cumulative step cost using get_travel_cost()
                step_cost = neighbor_zone.get_travel_cost()
                new_cost = current_cost + step_cost

                # Relaxation step: update shortest known distance
                if new_cost < distances.get(neighbor_name, float("inf")):
                    distances[neighbor_name] = new_cost
                    previous[neighbor_name] = current_name
                    heapq.heappush(pq, (new_cost, neighbor_name))

        # 3. Path Reconstruction
        if end_zone.name not in previous:
            return None  # Target unreachable

        path: List[str] = []
        curr: Optional[str] = end_zone.name
        while curr is not None:
            path.append(curr)
            curr = previous[curr]

        # Reverse path to get [start_zone -> ... -> end_zone] order
        path.reverse()
        return path
