import math
import os
import zipfile
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

SQRT2 = math.sqrt(2.0)

PASSABLE_CHARS = frozenset(".GS")
BLOCKED_CHARS = frozenset("@OTW")

# dx, dy, cost ; the first four are orthogonal, the last four diagonal
_MOVES = (
    (0, -1, 1.0), (0, 1, 1.0), (-1, 0, 1.0), (1, 0, 1.0),
    (-1, -1, SQRT2), (1, -1, SQRT2), (-1, 1, SQRT2), (1, 1, SQRT2),
)

# Reading text from a plain file or from inside a zip
def _read_text(path: str) -> str:
    """Read a text file, transparently opening it from a .zip if needed."""
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if len(names) != 1:
                raise ValueError(f"{path}: expected exactly 1 file in zip, found {names}")
            return zf.read(names[0]).decode("utf-8", errors="replace")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# Map
class GridMap:
    """A 2D grid stored as a flat bytearray (1 = passable, 0 = blocked)."""

    def __init__(self, width: int, height: int, cells: bytearray, name: str = ""):
        if len(cells) != width * height:
            raise ValueError("cells length does not match width*height")
        self.width = width
        self.height = height
        self.cells = cells
        self.name = name

    #basic queries 
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_passable(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and self.cells[y * self.width + x] == 1

    def num_passable(self) -> int:
        return sum(self.cells)

    def index(self, x: int, y: int) -> int:
        """Flat index for (x, y); handy for array-based closed/g-value tables."""
        return y * self.width + x

    def coords(self, idx: int) -> Tuple[int, int]:
        return idx % self.width, idx // self.width

    #successor generation (used by A* / weighted A*
    def neighbors(
        self,
        x: int,
        y: int,
        allow_diagonal: bool = True,
        allow_corner_cutting: bool = False,
    ) -> Iterator[Tuple[int, int, float]]:
        """Yield (nx, ny, step_cost) for each legal move out of (x, y)."""
        n = 8 if allow_diagonal else 4
        for dx, dy, cost in _MOVES[:n]:
            nx, ny = x + dx, y + dy
            if not self.is_passable(nx, ny):
                continue
            if dx != 0 and dy != 0 and not allow_corner_cutting:
                # diagonal: both side cells must be free
                if not (self.is_passable(x + dx, y) and self.is_passable(x, y + dy)):
                    continue
            yield nx, ny, cost

    def __repr__(self) -> str:
        return f"GridMap({self.name!r}, {self.width}x{self.height}, {self.num_passable()} passable)"


def parse_map(text: str, name: str = "") -> GridMap:
    "Parse the contents of a Moving AI .map file."
    lines = text.splitlines()
    height = width = None
    i = 0
    # header: scan until the line that says "map"
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line == "map":
            break
        parts = line.split()
        if len(parts) == 2:
            key, val = parts[0].lower(), parts[1]
            if key == "height":
                height = int(val)
            elif key == "width":
                width = int(val)
    else:
        raise ValueError("map header: missing 'map' line")

    if height is None or width is None:
        raise ValueError("map header: missing height or width")

    rows = [ln.rstrip("\r\n") for ln in lines[i:i + height]]
    if len(rows) != height:
        raise ValueError(f"expected {height} map rows, found {len(rows)}")

    cells = bytearray(width * height)
    for y, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"row {y}: expected width {width}, got {len(row)}")
        base = y * width
        for x, ch in enumerate(row):
            if ch in PASSABLE_CHARS:
                cells[base + x] = 1
            elif ch in BLOCKED_CHARS:
                cells[base + x] = 0
            else:
                raise ValueError(f"row {y}, col {x}: unknown map character {ch!r}")
    return GridMap(width, height, cells, name)


def load_map(path: str) -> GridMap:
    "Load a .map file into a GridMap"
    return parse_map(_read_text(path), name=os.path.basename(path))

# Scenarios
@dataclass(frozen=True)
class Scenario:
    bucket: int
    map_name: str
    width: int
    height: int
    start: Tuple[int, int]   
    goal: Tuple[int, int]    
    optimal_length: float


def parse_scenarios(text: str) -> List[Scenario]:
    "Parse the contents of a .scen file."
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines or not lines[0].lower().startswith("version"):
        raise ValueError("scenario file: missing 'version' header")
    out: List[Scenario] = []
    for lineno, ln in enumerate(lines[1:], start=2):
        parts = ln.split()  # tab or whitespace separated
        if len(parts) != 9:
            raise ValueError(f"scenario line {lineno}: expected 9 fields, got {len(parts)}")
        out.append(
            Scenario(
                bucket=int(parts[0]),
                map_name=parts[1],
                width=int(parts[2]),
                height=int(parts[3]),
                start=(int(parts[4]), int(parts[5])),
                goal=(int(parts[6]), int(parts[7])),
                optimal_length=float(parts[8]),
            )
        )
    return out


def load_scenarios(path: str) -> List[Scenario]:
    "Load a .scen file"
    return parse_scenarios(_read_text(path))

# Validation / preprocessing
def validate_scenarios(grid: GridMap, scenarios: List[Scenario]) -> List[Scenario]:
    """Keep only scenarios that matches the map, and start and goal are in bounds and passable. 
    Raises if nothing usable remains."""
    good = []
    for s in scenarios:
        if (s.width, s.height) != (grid.width, grid.height):
            continue
        if grid.is_passable(*s.start) and grid.is_passable(*s.goal):
            good.append(s)
    dropped = len(scenarios) - len(good)
    if dropped:
        print(f"[validate] dropped {dropped}/{len(scenarios)} invalid scenarios for {grid.name}")
    if not good:
        raise ValueError(f"no valid scenarios for {grid.name}")
    return good


def load_instance(map_path: str, scen_path: str) -> Tuple[GridMap, List[Scenario]]:
    "Load a map and its validated scenarios from the given paths."
    grid = load_map(map_path)
    scens = validate_scenarios(grid, load_scenarios(scen_path))
    return grid, scens


def summarize(grid: GridMap, scenarios: List[Scenario]) -> str:
    "Short text summary"
    total = grid.width * grid.height
    opt = [s.optimal_length for s in scenarios]
    buckets = sorted({s.bucket for s in scenarios})
    return (
        f"{grid.name}: {grid.width}x{grid.height}, "
        f"{grid.num_passable()} passable of {total} cells "
        f"({100.0 * grid.num_passable() / total:.1f}%), "
        f"{len(scenarios)} scenarios in {len(buckets)} buckets, "
        f"optimal length min/mean/max = {min(opt):.1f}/{sum(opt) / len(opt):.1f}/{max(opt):.1f}"
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usage: python gridmap.py <file.map[.zip]> <file.scen | file.map-scen.zip>")
        sys.exit(1)
    g, sc = load_instance(sys.argv[1], sys.argv[2])
    print(summarize(g, sc))