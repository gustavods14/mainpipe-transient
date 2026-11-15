"""Computational mesh and output stations (plan 01 M4, M14, U-07, U-08).

The MOC runs on the computational nodes x_i = L*i/N. Results are reported on the
*stations*: nodes plus profile vertices (U-07), sorted, a vertex closer than 1e-9*L to
a node being merged into that node. At a vertex that is not a node, H is interpolated
linearly between the two neighbouring nodes at every step; its elevation is the vertex
elevation. Q is never interpolated (U-07 amendment, D-57).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = [
    "MAX_STEPS",
    "N_REACHES_MIN",
    "N_REACHES_MAX",
    "Mesh",
    "build_horizontal_mesh",
    "build_profile_mesh",
    "time_step_s",
    "count_steps",
    "default_duration_s",
    "max_even_reaches",
]

MAX_STEPS = 10_000  # U-09, D-57
N_REACHES_MIN = 10  # U-09, HU-1.7
N_REACHES_MAX = 200

# U-08: absorbs binary noise in T/dt. Example: L = 1000 m, a = 1000 m/s, N = 26 gives
# dt = 0.0384615..., and 1.0 / dt = 26.000000000000004; without the tolerance a 1 s
# simulation would take 27 steps instead of 26.
_STEP_TOLERANCE = 1e-9
# U-07: a profile vertex closer than this fraction of L to a node is merged into the node.
_MERGE_TOLERANCE = 1e-9


@dataclass(frozen=True)
class Mesh:
    """Courant-1 mesh (dx = L/N, dt = dx/a, nodes x_i = L*i/N) and its output stations.

    ``x_m`` / ``elevation_m`` describe the N + 1 computational nodes. ``station_*``
    describe the output stations (nodes plus profile vertices, U-07); the head at
    station s is ``H[left[s]] + weight[s] * (H[right[s]] - H[left[s]])``, with
    ``left == right`` and ``weight == 0`` at a node, so node values are copied exactly.
    """

    length_m: float
    n_reaches: int
    dx_m: float
    dt_s: float
    x_m: np.ndarray  # node positions, length N + 1
    elevation_m: np.ndarray  # z at each node
    station_x_m: np.ndarray
    station_elevation_m: np.ndarray
    station_is_node: np.ndarray  # bool
    station_left: np.ndarray  # int node index
    station_right: np.ndarray  # int node index
    station_weight: np.ndarray  # in [0, 1)

    @property
    def midpoint_index(self) -> int:
        """Node at x = L/2 (N is even)."""
        return self.n_reaches // 2

    @property
    def stations_are_nodes(self) -> bool:
        """True when no profile vertex falls between nodes (stations == nodes)."""
        return bool(self.station_is_node.all())

    def station_head(self, node_head: np.ndarray) -> np.ndarray:
        """Head at every station from the head at the nodes (M14)."""
        if self.stations_are_nodes:
            return node_head
        left = node_head[self.station_left]
        return left + self.station_weight * (node_head[self.station_right] - left)


def time_step_s(length_m: float, n_reaches: int, wave_speed_ms: float) -> float:
    """dt = (L/N)/a, evaluated exactly as the mesh does (Courant = 1)."""
    return (length_m / n_reaches) / wave_speed_ms


def _node_positions(length_m: float, n_reaches: int) -> np.ndarray:
    x = length_m * np.arange(n_reaches + 1, dtype=float) / n_reaches
    x[-1] = length_m  # last node is L exactly (U-07)
    return x


def _frozen(*arrays: np.ndarray) -> None:
    for arr in arrays:
        arr.setflags(write=False)


def build_horizontal_mesh(
    length_m: float, n_reaches: int, wave_speed_ms: float, pipe_elevation_m: float
) -> Mesh:
    dx = length_m / n_reaches
    dt = time_step_s(length_m, n_reaches, wave_speed_ms)
    x = _node_positions(length_m, n_reaches)
    z = np.full(n_reaches + 1, float(pipe_elevation_m))
    idx = np.arange(n_reaches + 1)
    is_node = np.ones(n_reaches + 1, dtype=bool)
    weight = np.zeros(n_reaches + 1)
    _frozen(x, z, idx, is_node, weight)
    return Mesh(
        length_m=length_m, n_reaches=n_reaches, dx_m=dx, dt_s=dt, x_m=x, elevation_m=z,
        station_x_m=x, station_elevation_m=z, station_is_node=is_node,
        station_left=idx, station_right=idx, station_weight=weight,
    )


def build_profile_mesh(
    profile_x_m: list[float], profile_z_m: list[float], n_reaches: int, wave_speed_ms: float
) -> Mesh:
    """Mesh over the profile: L = last chainage, z linear between vertices (M13, M14, U-07).

    ``profile_x_m`` starts at 0 and is strictly increasing (validated by the contract).
    """
    px = np.asarray(profile_x_m, dtype=float)
    pz = np.asarray(profile_z_m, dtype=float)
    length_m = float(px[-1])
    dx = length_m / n_reaches
    dt = time_step_s(length_m, n_reaches, wave_speed_ms)
    x = _node_positions(length_m, n_reaches)
    z = np.interp(x, px, pz)

    # Classify each vertex: merged into its nearest node, or a station of its own.
    nearest = np.clip(np.rint(px / dx).astype(np.int64), 0, n_reaches)
    merged = np.abs(px - x[nearest]) < _MERGE_TOLERANCE * length_m
    # A merged vertex keeps its own elevation at the node (the vertex is the high point).
    z[nearest[merged]] = pz[merged]

    free_x = px[~merged]
    free_z = pz[~merged]
    st_x = np.concatenate([x, free_x])
    st_z = np.concatenate([z, free_z])
    st_node = np.concatenate([np.ones(n_reaches + 1, dtype=bool), np.zeros(free_x.size, dtype=bool)])
    nodes = np.arange(n_reaches + 1)
    left_free = np.clip(np.searchsorted(x, free_x, side="right") - 1, 0, n_reaches - 1)
    right_free = left_free + 1
    weight_free = (free_x - x[left_free]) / (x[right_free] - x[left_free])
    st_left = np.concatenate([nodes, left_free])
    st_right = np.concatenate([nodes, right_free])
    st_weight = np.concatenate([np.zeros(n_reaches + 1), weight_free])

    order = np.argsort(st_x, kind="stable")
    st_x, st_z, st_node = st_x[order], st_z[order], st_node[order]
    st_left, st_right, st_weight = st_left[order], st_right[order], st_weight[order]
    _frozen(x, z, st_x, st_z, st_node, st_left, st_right, st_weight)
    return Mesh(
        length_m=length_m, n_reaches=n_reaches, dx_m=dx, dt_s=dt, x_m=x, elevation_m=z,
        station_x_m=st_x, station_elevation_m=st_z, station_is_node=st_node,
        station_left=st_left, station_right=st_right, station_weight=st_weight,
    )


def count_steps(duration_s: float, dt_s: float) -> int:
    """n_steps = ceil(T/dt - 1e-9) (U-08)."""
    return math.ceil(duration_s / dt_s - _STEP_TOLERANCE)


def default_duration_s(closure_duration_s: float, length_m: float, wave_speed_ms: float) -> float:
    """Tc + 5 * (4L/a) (plan 01 §1.3)."""
    return closure_duration_s + 5.0 * (4.0 * length_m / wave_speed_ms)


def max_even_reaches(duration_s: float, length_m: float, wave_speed_ms: float) -> int | None:
    """Largest even N in [10, 200] whose step count for ``duration_s`` fits MAX_STEPS."""
    for n in range(N_REACHES_MAX, N_REACHES_MIN - 1, -2):
        if count_steps(duration_s, time_step_s(length_m, n, wave_speed_ms)) <= MAX_STEPS:
            return n
    return None
