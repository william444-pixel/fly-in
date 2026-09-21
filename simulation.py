from typing import Dict, List
from graph import Drone, Graph, Zone, RestrictedZone


class SimulationEngine:

    def __init__(
        self,
        graph: Graph,
        nb_drones: int,
        drone_paths: Dict[int, List[str]]
    ) -> None:
        self.graph: Graph = graph
        self.nb_drones: int = nb_drones
        self.drone_paths: Dict[int, List[Zone]] = {}

        for drone_id, path_names in drone_paths.items():
            self.drone_paths[drone_id] = [
                self.graph.zones[name]
                for name in path_names
                if name in self.graph.zones
            ]
        self.drones: List[Drone] = []
        self.drone_path_indices: Dict[int, int] = {}
        self.current_time_step: int = 0
        for drone_id in range(1, nb_drones + 1):
            drone = Drone(drone_id=drone_id)
            self.drones.append(drone)
            self.drone_path_indices[drone.id] = 0

            paths = self.drone_paths.get(drone_id, [])
            if paths:
                start_zone = paths[0]
                start_zone.add_drone(drone)

    def is_simulation_complete(self) -> bool:
        if not self.drones:
            return True
        return all(drone.is_finished for drone in self.drones)

    def step(self) -> Dict[str, str]:
        self.current_time_step += 1
        step_log: Dict[str, str] = {}
        for connection in self.graph.connections:
            connection.reset_turn()

        if self.current_time_step > 500:
            for drone in self.drones:
                drone.is_finished = True
            return step_log

        sorted_drones = sorted(
            self.drones,
            key=lambda d: self.drone_path_indices.get(d.id, 0),
            reverse=True
        )

        for drone in sorted_drones:
            if drone.is_finished:
                continue

            path = self.drone_paths.get(drone.id, [])
            if not path:
                continue

            end_zone = path[-1]

            if drone.transit_turns_left > 0:
                drone.transit_turns_left -= 1
                if drone.transit_turns_left == 0 and drone.target_zone:
                    if drone.current_zone:
                        drone.current_zone.remove_drone(drone)
                    drone.target_zone.add_drone(drone)
                    step_log[drone.name] = drone.target_zone.name

                    if drone.target_zone == end_zone:
                        drone.is_finished = True
                        drone.target_zone.remove_drone(drone)

                    drone.target_zone = None
                continue

            current_idx = self.drone_path_indices[drone.id]
            current_zone = path[current_idx]

            if current_zone == end_zone:
                drone.is_finished = True
                current_zone.remove_drone(drone)
                continue

            if current_idx + 1 >= len(path):
                continue

            next_zone = path[current_idx + 1]

            connection = None
            for neighbor, conn in self.graph.get_neighbors(current_zone):
                if neighbor == next_zone:
                    connection = conn
                    break

            if next_zone != end_zone:
                incoming_drones = sum(
                    1 for d in self.drones 
                    if d.target_zone == next_zone and d.transit_turns_left > 0
                )
                if len(next_zone.occupants) + incoming_drones >= next_zone.max_drones:
                    continue
            
            if connection and not connection.can_traverse():
                continue

            if isinstance(next_zone, RestrictedZone):
                drone.transit_turns_left = 1
                drone.target_zone = next_zone
                self.drone_path_indices[drone.id] = current_idx + 1
                if connection:
                    connection.current_traversals += 1
                step_log[drone.name] = f"{current_zone.name}-{next_zone.name}"
            else:
                current_zone.remove_drone(drone)
                next_zone.add_drone(drone)
                self.drone_path_indices[drone.id] = current_idx + 1
                if connection:
                    connection.current_traversals += 1

                step_log[drone.name] = next_zone.name
                if next_zone == end_zone:
                    drone.is_finished = True
                    next_zone.remove_drone(drone)
        return step_log