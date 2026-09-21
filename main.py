import sys
from typing import List
from dijkstra import Pathfinder
from graph import TerminalColors
from parsing import MapParser, ParsingError
from simulation import SimulationEngine


def main() -> None:
# 2. Filter sys.argv bash t-jbed l-path d map
    args = [arg for arg in sys.argv[1:]]
    # show_capacity = "--capacity-info" in args
    # if "--capacity-info" not in args:
    #     print("Usage: python main.py [--capacity-info] <map_file_path>")
    #     sys.exit(1)

    map_path = args[0]

    try:
        parser = MapParser(map_path)
        graph, nb_drones = parser.parse()
    except (ParsingError, FileNotFoundError) as e:
        print(f"Error loading map: {e}")
        sys.exit(1)

    if not graph.start_hub or not graph.end_hub:
        print("Error: Map must contain both a start_hub and an end_hub.")
        sys.exit(1)

    pathfinder = Pathfinder(graph)
    available_paths = pathfinder.find_multiple_paths(
        graph.start_hub, graph.end_hub, max_paths=3
    )

    if not available_paths:
        print("Error: No valid path found from start to end.")
        sys.exit(1)

    drone_paths = pathfinder.assign_paths_to_drones(available_paths, nb_drones)

    sim = SimulationEngine(
        graph=graph, nb_drones=nb_drones, drone_paths=drone_paths
    )

    while not sim.is_simulation_complete():
        moves = sim.step()

        turn_output: List[str] = []
        for drone_name, zone_name in moves.items():
            if "-" in zone_name:
                parts = zone_name.split("-")
                colored_parts = []
                for p in parts:
                    z_color = graph.zones[p].color if p\
                        in graph.zones else "none"
                    colored_parts.append(TerminalColors.colorize(p, z_color))
                colored_zone = "-".join(colored_parts)
            else:
                zone_color = (
                    graph.zones[zone_name].color
                    if zone_name in graph.zones
                    else "none"
                )
                colored_zone = TerminalColors.colorize(zone_name, zone_color)

            turn_output.append(f"{drone_name}-{colored_zone}")

        if turn_output:
            print(" ".join(turn_output))
    #     if show_capacity:
    # # 1. Zone capacity info
    #         for z_name, zone in graph.zones.items():
    #             if len(zone.occupants) > 0:
    #              print(f"{z_name}: {len(zone.occupants)}/{zone.max_drones} drones")
    # # 2. Connection capacity info
    #         for conn in graph.connections:
    #             if conn.current_traversals > 0:
    #                 print(f"{conn.zone1.name}-{conn.zone2.name}: {conn.current_traversals}/{conn.max_link_capacity} capacity used")


if __name__ == "__main__":
    main()
