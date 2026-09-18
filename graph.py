from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class Drone:
    """Represents an autonomous drone in the simulation."""

    def __init__(self, drone_id: int) -> None:
        self.id: int = drone_id
        self.name: str = f"D{drone_id}"
        self.current_zone: Optional["Zone"] = None
        self.target_zone: Optional["Zone"] = None
        self.transit_turns_left: int = 0
        self.is_finished: bool = False

    def __repr__(self) -> str:
        return self.name


class Zone(ABC):
    """Abstract Base Class representing a zone (node) in the graph."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "none",
        max_drones: int = 1
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.color: str = color
        self.max_drones: int = max_drones
        self.occupants: List[Drone] = []

    def has_capacity(self) -> bool:
        """Check if the zone can accept another drone."""
        return len(self.occupants) < self.max_drones

    def add_drone(self, drone: Drone) -> None:
        """Add a drone to this zone."""
        if drone not in self.occupants:
            self.occupants.append(drone)
            drone.current_zone = self

    def remove_drone(self, drone: Drone) -> None:
        """Remove a drone from this zone."""
        if drone in self.occupants:
            self.occupants.remove(drone)

    @abstractmethod
    def get_travel_cost(self) -> int:
        """Return movement cost in turns to enter this zone."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class NormalZone(Zone):
    """Standard zone with 1 turn movement cost."""

    def get_travel_cost(self) -> int:
        return 1


class PriorityZone(Zone):
    """Priority zone with 1 turn cost, prioritized in pathfinding."""

    def get_travel_cost(self) -> int:
        return 1


class RestrictedZone(Zone):
    """Restricted zone requiring 2 turns to be reached."""

    def get_travel_cost(self) -> int:
        return 2


class BlockedZone(Zone):
    """Inaccessible zone that drones must not enter."""

    def has_capacity(self) -> bool:
        return False

    def get_travel_cost(self) -> int:
        return 999999  # Infinite cost representation


class StartZone(Zone):
    """Start zone with unlimited capacity."""

    def has_capacity(self) -> bool:
        return True

    def get_travel_cost(self) -> int:
        return 1


class EndZone(Zone):
    """Target end zone with unlimited capacity."""

    def has_capacity(self) -> bool:
        return True

    def get_travel_cost(self) -> int:
        return 1


class Connection:
    """Represents a bidirectional edge
      between two zones with capacity limits."""

    def __init__(
        self,
        zone1: Zone,
        zone2: Zone,
        max_link_capacity: int = 1
    ) -> None:
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_link_capacity
        self.current_traversals: int = 0

    def get_other(self, zone: Zone) -> Zone:
        """Given one end of the connection, return the other end."""
        if zone == self.zone1:
            return self.zone2
        elif zone == self.zone2:
            return self.zone1
        raise ValueError(f"Zone {zone.name} is not part of this connection")

    def can_traverse(self) -> bool:
        """Check if connection has capacity
        for another traversal in current turn."""
        return self.current_traversals < self.max_link_capacity

    def reset_turn(self) -> None:
        """Reset traversal counter for a new turn."""
        self.current_traversals = 0


class Graph:
    """Manages the network topology and spatial connections."""

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.adj_list: Dict[str, List[Tuple[Zone, Connection]]] = {}
        self.start_hub: Optional[StartZone] = None
        self.end_hub: Optional[EndZone] = None

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph network."""
        self.zones[zone.name] = zone
        if zone.name not in self.adj_list:
            self.adj_list[zone.name] = []

        if isinstance(zone, StartZone):
            self.start_hub = zone
        elif isinstance(zone, EndZone):
            self.end_hub = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a bidirectional link between two zones."""
        self.connections.append(connection)
        z1 = connection.zone1
        z2 = connection.zone2

        self.adj_list[z1.name].append((z2, connection))
        self.adj_list[z2.name].append((z1, connection))

    def get_neighbors(self, zone: Zone) -> List[Tuple[Zone, Connection]]:
        """Retrieve reachable adjacent zones and their connecting edge."""
        return self.adj_list.get(zone.name, [])


class TerminalColors:
    """ANSI color codes for extensive terminal output visualization."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Default color for zones with missing or unspecified color
    DEFAULT_COLOR = "\033[96m"  # Bright Cyan

    COLORS = {
        # Standard basic colors
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "black": "\033[30;1m",
        "orange": "\033[38;5;208m",
        "purple": "\033[38;5;129m",
        "pink": "\033[38;5;206m",
        "brown": "\033[38;5;130m",
        "maroon": "\033[38;5;88m",
        "gold": "\033[38;5;220m",
        "darkred": "\033[38;5;52m",
        "violet": "\033[38;5;135m",
        "crimson": "\033[38;5;196m",
    }

    @classmethod
    def colorize(cls, text: str, color_name: str) -> str:
        """Wrap text with ANSI color
        codes based on color name, fallback to DEFAULT_COLOR."""
        if not color_name or color_name.lower() in ("none", "null", ""):
            return f"{cls.DEFAULT_COLOR}{cls.BOLD}{text}{cls.RESET}"

        color_code = cls.COLORS.get(color_name.lower(), cls.DEFAULT_COLOR)
        return f"{color_code}{cls.BOLD}{text}{cls.RESET}"
