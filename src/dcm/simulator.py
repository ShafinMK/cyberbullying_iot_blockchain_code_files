from __future__ import annotations
import os
from dataclasses import dataclass
from ..config import Config, seeded_rng

@dataclass
class SyntheticBatch:
    texts: list[bytes]
    locations: list[bytes]
    audio_meta: list[bytes]
    audio_blobs: list[bytes]

def generate_batch(cfg: Config, n_incidents: int, tag: str = "sim") -> SyntheticBatch:
    rng = seeded_rng(cfg, tag)
    mix = cfg["workload"]["evidence_mix"]
    sizes = cfg["workload"]["packet_sizes_b"]
    texts, locs, metas, blobs = [], [], [], []
    for _ in range(n_incidents):
        u = rng.random()
        if u < mix["text"]:
            texts.append(os.urandom(sizes["text"]))
        elif u < mix["text"] + mix["location"]:
            locs.append(os.urandom(sizes["location"]))
        else:
            metas.append(os.urandom(sizes["audio_metadata"]))
            if rng.random() < 0.5:
                blobs.append(os.urandom(160 * 1024))
    return SyntheticBatch(texts, locs, metas, blobs)