import sys
from typing import List
from dijkstra import Pathfinder
from graph import TerminalColors
from parsing import MapParser, ParsingError
from simulation import SimulationEngine


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file_path>")
        sys.exit(1)

    map_path = sys.argv[1]

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
        graph.start_hub, graph.end_hub, max_paths=5
    )

    if not available_paths:
        print("Error: No valid path found from start to end.")
        sys.exit(1)  # دابا راه فـ داخل الـ if

    drone_paths = pathfinder.assign_paths_to_drones(available_paths, nb_drones)

    # 3. تشغيل المحاكاة واستعمال drone_paths بدلاً من path_names
    sim = SimulationEngine(
        graph=graph, nb_drones=nb_drones, drone_paths=drone_paths
    )

    while not sim.is_simulation_complete():
        moves = sim.step()

        turn_output: List[str] = []
        for drone_name, zone_name in moves.items():
            # التعامل مع الانتقال بين منطقتين (zone1-zone2 فـ RestrictedZone)
            if "-" in zone_name:
                parts = zone_name.split("-")
                colored_parts = []
                for p in parts:
                    z_color = graph.zones[p].color if p in graph.zones else "none"
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


if __name__ == "__main__":
    main()