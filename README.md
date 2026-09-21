# Fly-in 🛸

Fly-in is an autonomous drone network routing and discrete-event simulation engine built in Python for 1337[cite: 2, 5]. The project reads custom map files, calculates optimal paths across complex terrains, balances traffic across multiple routes, and executes turn-by-turn drone movements while respecting spatial and capacity constraints[cite: 1, 5, 7].

---

## Description

The main goal of **Fly-in** is to simulate moving a fleet of autonomous drones from a starting hub (`StartZone`) to a target destination (`EndZone`) in the fewest turns possible without exceeding zone capacities or link limits[cite: 2, 5, 7].

### Overview of Functionality
* **Map Parsing & Validation**: Reads network files, parses metadata tags (`color`, `max_drones`, `max_link_capacity`), and validates graph integrity (e.g., detecting duplicate coordinates or isolated hubs)[cite: 5].
* **Network Graph Representation**: Constructs an object-oriented graph with polymorphic zone types, connections, and drones.
* **Multi-Route Pathfinding**: Uses priority-queue Dijkstra search combined with edge-exclusion heuristics to discover primary and alternative optimal routes.
* **Turn-Based Simulation Engine**: Manages discrete time steps, tracking active transit states, connection limits, and zone occupancy.
* **Visual Terminal Feedback**: Formats movement steps with ANSI terminal color codes corresponding to individual zone configurations.

---

## Instructions

# Prerequisites
* **Python 3.10+** (Uses Python Standard Library; optional development dependencies are listed in `requirements.txt`)[cite: 4, 6].

### Installation
Clone the repository and set up development/linting tools:

```bash
git clone [https://github.com/your-username/fly-in.git]
cd fly-in
make install
# Running the Program
python main.py maps/easy/01_simple.txt
# Run with default map
make run
# Run with a custom map path
make run MAP=maps/challenger/01_the_impossible_dream.txt
```
| Command | Action |
| :--- | :--- |
| `make run` | Runs the main simulation engine. |
| `make lint` | Executes flake8 and mypy strict type checking. |
| `make debug` | Runs the simulation inside the Python debugger (pdb). |
| `make clean` | Removes `__pycache__`, `.mypy_cache`, and temporary Python artifacts. |

# Algorithm Explanation
## Pathfinding Approach
* Shortest Path Search (Dijkstra):
Uses a min-priority queue (heapq) to compute path costs based on zone travel requirements:
PriorityZone: 0.5 turns (preferred fast route).NormalZone / StartZone / EndZone: 1 turn.
RestrictedZone: 2 turns.
BlockedZone: 999999 (inaccessible, skipped during search).
* Alternative Routes Generation:
To prevent traffic bottlenecks along a single path, the Pathfinder temporarily excludes edges along the primary route (excluded_edges) and re-runs Dijkstra to discover valid alternative routes.
* Traffic Distribution (Load Balancing):
The program filters paths that yield minimal total turn costs (min_turns) and assigns drones to best paths using a Modulo Round-Robin distribution ((drone_id - 1) % len(best_paths)).   

# Key Design Decisions
* Polymorphic Object-Oriented Architecture: Zones inherit from an abstract base class (Zone). Behaviors like capacity checks (has_capacity()) and travel costs (get_travel_cost()) are encapsulated within specific subclasses (NormalZone, RestrictedZone, etc.).
* Reverse Drone Execution Order: Drones are sorted in descending order by their current path index before each step (reverse=True). Drones furthest along their path move first, clearing capacity for drones following behind them.Multi-Tier Capacity Validation: Before a drone moves, the simulation validates:
1. Connection capacity (connection.can_traverse()).
2. Zone capacity (max_drones), taking into account drones currently in transit towards that zone.   

# Visual Representation
 * FeaturesThe project includes an ANSI-based visual feedback module (TerminalColors in graph.py):   Dynamic Zone Colorization: Terminal outputs wrap zone and route tokens with ANSI color codes defined directly in the map file (e.g., [color=cyan], [color=red], [color=gold]).
 * Transit State Formatting: When a drone enters a multi-turn RestrictedZone, the transition state is formatted with dual-color identifiers showing both origin and destination (e.g., D1-StartZone-RestrictedZone).
 #### How Visuals Enhance User Experience (UX)
 * Real-time Map Visibility: Color highlights make it easy to visually track different terrain types (e.g., gold for priority zones, red for restricted zones).
 * Clear Debugging & Evaluation: Evaluators can instantly spot drone collisions, congestion bottlenecks, or movement delays directly in the terminal without parsing raw text output.
 # Example Input and Expected Output
 ```bash
 nb_drones: 2

start_hub: Start 0 0 [color=green]
end_hub: Goal 4 0 [color=yellow]

hub: HubA 2 0 [normal color=cyan max_drones=1]
hub: HubB 2 2 [priority color=gold max_drones=1]

connection: Start-HubA [max_link_capacity=1]
connection: Start-HubB [max_link_capacity=1]
connection: HubA-Goal [max_link_capacity=1]
connection: HubB-Goal [max_link_capacity=1]
```
#### Execution Command
```bash 
python main.py maps/sample.txt
```
#### Expected Terminal Output
D1-HubA D2-HubB

D1-Goal D2-Goal