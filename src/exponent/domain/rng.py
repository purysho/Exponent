"""Deterministic randomness.

Every court cell gets its own generator, derived from (experiment key, cell
index, replication). Any single cell can be rerun alone, in any order or in
parallel, and give the same numbers. There is no global RNG state anywhere.
"""

from __future__ import annotations

import hashlib

import numpy as np


def _entropy(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:16], "little")


def cell_rng(key: str, *spawn_key: int) -> np.random.Generator:
    """Generator for one cell of an experiment named `key`."""
    seq = np.random.SeedSequence(entropy=_entropy(key), spawn_key=tuple(spawn_key))
    return np.random.default_rng(seq)
