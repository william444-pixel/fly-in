from typing import Dict, List, Optional
from graph import Connection, Drone, Graph, Zone


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

        for connection in self.graph.connections:
            connection.reset_turn()

        end_zone = self.path_zones[-1]

        for drone in self.drones:
            # Skip if drone is already finished
            if drone.is_finished:
                continue

            current_idx = self.drone_path_indices[drone.id]
            current_zone = drone.current_zone
            next_zone = self.path_zones[current_idx + 1]

            # Find connection
            connection: Optional[Connection] = None
            if current_zone:
                for neighbor, conn in self.graph.get_neighbors(current_zone):
                    if neighbor == next_zone:
                        connection = conn
                        break

            # Capacity checks
            can_move = True
            if not next_zone.has_capacity():
                can_move = False

            if connection and not connection.can_traverse():
                can_move = False

            # Move drone
            if can_move:
                if current_zone:
                    current_zone.remove_drone(drone)

                next_zone.add_drone(drone)
                self.drone_path_indices[drone.id] = current_idx + 1

                if connection:
                    connection.current_traversals += 1

                # Record ONLY the drones that actually moved this turn
                step_log[drone.name] = next_zone.name

                if next_zone == end_zone:
                    drone.is_finished = True

        return step_log