from __future__ import annotations
from ..config import Config
from .stake import random_validators
from .committee import select_committee, committee_size
from .pbft import run_pbft, max_faulty

class HybridConsensus:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.m = cfg["network"]["validators_m"]
        self.validators = random_validators(cfg, self.m)
        self.k = committee_size(self.m)
        self.round = 0
        self.committee = []
        self.selection_ms = 0.0
        self._reselect()

    def _reselect(self) -> None:
        self.committee = select_committee(self.cfg, self.validators, self.round)
        self.selection_ms = 50.0 + 10.0 * (self.round % 7)

    def step(self, faulty: int = 0) -> dict:
        if self.round % self.cfg["consensus"]["reselect_every_blocks"] == 0:
            self._reselect()
        res = run_pbft(self.k, faulty,
                       base_latency_ms=self.selection_ms,
                       prep_ms=120.0, commit_ms=60.0, ledger_ms=35.0)
        self.round += 1
        return {"round": self.round, "k": self.k, "committed": res.committed,
                "latency_ms": res.latency_ms, "faulty": faulty,
                "max_faulty": max_faulty(self.k), "selection_ms": self.selection_ms}