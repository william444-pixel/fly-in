from typing import Dict, List, Optional
from graph import Drone, Graph, Zone, RestrictedZone


class SimulationEngine:

    def __init__(
        self, graph: Graph, nb_drones: int, path_names: Optional[List[str]]
    ) -> None:
        self.graph: Graph = graph
        self.nb_drones: int = nb_drones
        self.path_names: List[str] = path_names or []

        self.path_zones: List[Zone] = [
            self.graph.zones[name]
            for name in self.path_names
            if name in self.graph.zones
        ]

        self.drones: List[Drone] = []
        self.drone_path_indices: Dict[int, int] = {}
        self.current_time_step: int = 0

        if self.path_zones:
            start_zone = self.path_zones[0]
            for drone_id in range(1, nb_drones + 1):
                drone = Drone(drone_id=drone_id)
                start_zone.add_drone(drone)
                self.drones.append(drone)
                self.drone_path_indices[drone.id] = 0

    def is_simulation_complete(self) -> bool:
        if not self.drones:
            return True
        return all(drone.is_finished for drone in self.drones)

    def step(self) -> Dict[str, str]:
        self.current_time_step += 1
        step_log: Dict[str, str] = {}

        if not self.path_zones:
            return step_log

        # Reset connection counters at start of turn
        for connection in self.graph.connections:
            connection.reset_turn()

        end_zone = self.path_zones[-1]

        for drone in self.drones:
            # 1. Skip completely finished drones
            if drone.is_finished:
                continue

            current_idx = self.drone_path_indices[drone.id]
            current_zone = self.path_zones[current_idx]

            if current_zone == end_zone:
                drone.is_finished = True
                current_zone.remove_drone(drone)
                continue

            if drone.transit_turns_left > 0:
                drone.transit_turns_left -= 1
                continue

            next_zone = self.path_zones[current_idx + 1]

            for neighbor, conn in self.graph.get_neighbors(current_zone):
                if neighbor == next_zone:
                    connection = conn
                    break

            # 4. Capacity Checks
            if len(next_zone.occupants) >= next_zone.max_drones:
                continue

            if connection and not connection.can_traverse():
                continue

            current_zone.remove_drone(drone)
            next_zone.add_drone(drone)
            self.drone_path_indices[drone.id] = current_idx + 1

            if connection:
                connection.current_traversals += 1

            step_log[drone.name] = next_zone.name

            if isinstance(next_zone, RestrictedZone):
                drone.transit_turns_left = 1

            if next_zone == end_zone:
                drone.is_finished = True
                next_zone.remove_drone(drone)
        return step_log
