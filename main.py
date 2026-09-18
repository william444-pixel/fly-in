import sys
from typing import List
from dijkstra import Pathfinder
from parsing import MapParser, ParsingError
from simulation import SimulationEngine
from graph import TerminalColors


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
    path = pathfinder.find_shortest_path(graph.start_hub, graph.end_hub)

    if not path:
        print("Error: No valid path found between start_hub and end_hub.")
        sys.exit(1)

    sim = SimulationEngine(graph=graph, nb_drones=nb_drones, path_names=path)

    while not sim.is_simulation_complete():
        moves = sim.step()

        turn_output: List[str] = []
        for drone_name, zone_name in moves.items():
            # Get zone color from graph metadata
            zone_color = graph.zones[zone_name].color \
                if zone_name in graph.zones else "none"

            colored_zone = TerminalColors.colorize(zone_name, zone_color)
            turn_output.append(f"{drone_name}-{colored_zone}")

        if turn_output:
            print(" ".join(turn_output))


if __name__ == "__main__":
    main()
