"""Map parser module for the Fly-in project.

Parses custom network map files and constructs the Graph structure.
Handles errors with clear feedback on line number and root cause.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from graph import (
    BlockedZone,
    Connection,
    EndZone,
    Graph,
    NormalZone,
    PriorityZone,
    RestrictedZone,
    StartZone,
    Zone,
)


class ParsingError(Exception):
    """Custom exception raised when map parsing fails."""

    def __init__(self, line_number: int, message: str) -> None:
        self.line_number: int = line_number
        self.message: str = message
        super().__init__(f"Parsing Error on line {line_number}: {message}")


class MapParser:
    """Parser for Fly-in network map files."""

    def __init__(self, file_path: str) -> None:
        self.file_path: Path = Path(file_path)
        self.nb_drones: int = 0
        self.seen_connections: Set[Tuple[str, str]] = set()

    def parse(self) -> Tuple[Graph, int]:
        """Parse the input file and return a Graph object and total drones count.

        Raises:
            ParsingError: If any formatting or constraint violation occurs.
            FileNotFoundError: If the file does not exist.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        graph = Graph()
        lines = self.file_path.read_text(encoding="utf-8").splitlines()

        has_start = False
        has_end = False

        for idx, raw_line in enumerate(lines, start=1):
            line = self._clean_line(raw_line)
            if not line:
                continue

            if idx == 1 or self.nb_drones == 0:
                if line.startswith("nb_drones:"):
                    self.nb_drones = self._parse_nb_drones(line, idx)
                    continue
                else:
                    raise ParsingError(
                        idx, "First non-empty line must define 'nb_drones: <number>'"
                    )

            if line.startswith("start_hub:"):
                if has_start:
                    raise ParsingError(idx, "Multiple start_hub definitions found")
                zone = self._parse_zone_line(line, idx, zone_kind="start")
                graph.add_zone(zone)
                has_start = True

            elif line.startswith("end_hub:"):
                if has_end:
                    raise ParsingError(idx, "Multiple end_hub definitions found")
                zone = self._parse_zone_line(line, idx, zone_kind="end")
                graph.add_zone(zone)
                has_end = True

            elif line.startswith("hub:"):
                zone = self._parse_zone_line(line, idx, zone_kind="normal")
                if zone.name in graph.zones:
                    raise ParsingError(idx, f"Duplicate zone name '{zone.name}'")
                graph.add_zone(zone)

            elif line.startswith("connection:"):
                conn = self._parse_connection_line(line, idx, graph.zones)
                graph.add_connection(conn)

            else:
                raise ParsingError(idx, f"Unknown syntax line format: '{line}'")

        # Final Graph Validation
        if not has_start:
            raise ParsingError(len(lines), "Missing mandatory 'start_hub'")
        if not has_end:
            raise ParsingError(len(lines), "Missing mandatory 'end_hub'")

        return graph, self.nb_drones

    def _clean_line(self, line: str) -> str:
        """Strip comments starting with '#' and trailing spaces."""
        line = line.split("#", 1)[0]
        return line.strip()

    def _parse_nb_drones(self, line: str, line_num: int) -> int:
        parts = line.split(":")
        if len(parts) != 2:
            raise ParsingError(line_num, "Invalid nb_drones format")
        try:
            val = int(parts[1].strip())
            if val <= 0:
                raise ValueError()
            return val
        except ValueError:
            raise ParsingError(
                line_num, "nb_drones must be a positive non-zero integer"
            )

    def _extract_metadata(self, line: str) -> Tuple[str, Dict[str, str]]:
        """Extract main segment and metadata key-values inside [] brackets."""
        bracket_match = re.search(r"\[(.*?)\]", line)
        metadata: Dict[str, str] = {}

        if bracket_match:
            meta_str = bracket_match.group(1)
            main_part = line[: bracket_match.start()].strip()
            # Parse key=value or standalone tags
            for token in meta_str.split():
                if "=" in token:
                    k, v = token.split("=", 1)
                    metadata[k.strip()] = v.strip()
                elif token in ("normal", "blocked", "restricted", "priority"):
                    metadata["zone"] = token
                else:
                    metadata[token] = "true"
        else:
            main_part = line.strip()

        return main_part, metadata

    def _parse_zone_line(self, line: str, line_num: int, zone_kind: str) -> Zone:
        main_part, metadata = self._extract_metadata(line)
        tokens = main_part.split()

        if len(tokens) < 4:
            raise ParsingError(
                line_num, f"Invalid zone definition format: '{line}'"
            )

        name = tokens[1]
        if "-" in name or " " in name:
            raise ParsingError(
                line_num, f"Zone name '{name}' contains forbidden '-' or spaces"
            )

        try:
            x = int(tokens[2])
            y = int(tokens[3])
        except ValueError:
            raise ParsingError(line_num, "Zone coordinates x and y must be integers")

        color = metadata.get("color", "none")
        zone_type = metadata.get("zone", "normal")

        try:
            max_drones = int(metadata.get("max_drones", 1))
            if max_drones <= 0:
                raise ValueError()
        except ValueError:
            raise ParsingError(line_num, "max_drones must be a positive integer")

        if zone_kind == "start":
            return StartZone(name, x, y, color=color)
        elif zone_kind == "end":
            return EndZone(name, x, y, color=color)

        if zone_type == "normal":
            return NormalZone(name, x, y, color=color, max_drones=max_drones)
        elif zone_type == "priority":
            return PriorityZone(name, x, y, color=color, max_drones=max_drones)
        elif zone_type == "restricted":
            return RestrictedZone(name, x, y, color=color, max_drones=max_drones)
        elif zone_type == "blocked":
            return BlockedZone(name, x, y, color=color, max_drones=max_drones)
        else:
            raise ParsingError(
                line_num,
                f"Unknown zone type '{zone_type}'. Allowed: normal, priority, restricted, blocked",
            )

    def _parse_connection_line(
        self, line: str, line_num: int, zones: Dict[str, Zone]
    ) -> Connection:
        main_part, metadata = self._extract_metadata(line)
        tokens = main_part.split()

        if len(tokens) < 2:
            raise ParsingError(line_num, "Invalid connection format")

        conn_str = tokens[1]
        if "-" not in conn_str:
            raise ParsingError(
                line_num, "Connection syntax must be 'zone1-zone2'"
            )

        z1_name, z2_name = conn_str.split("-", 1)

        if z1_name not in zones:
            raise ParsingError(
                line_num, f"Connection references unknown zone '{z1_name}'"
            )
        if z2_name not in zones:
            raise ParsingError(
                line_num, f"Connection references unknown zone '{z2_name}'"
            )

        # Check for duplicated bidirectional connection
        pair = (min(z1_name, z2_name), max(z1_name, z2_name))
        if pair in self.seen_connections:
            raise ParsingError(
                line_num, f"Duplicate connection detected between {z1_name} and {z2_name}"
            )
        self.seen_connections.add(pair)

        try:
            max_capacity = int(metadata.get("max_link_capacity", 1))
            if max_capacity <= 0:
                raise ValueError()
        except ValueError:
            raise ParsingError(
                line_num, "max_link_capacity must be a positive integer"
            )

        return Connection(zones[z1_name], zones[z2_name], max_link_capacity=max_capacity)