from __future__ import annotations
from dataclasses import dataclass

@dataclass
class TriggerWindow:
    start: float
    end: float
    def contains(self, t: float) -> bool:
        return self.start <= t <= self.end

def incident_window(center: float, before_s: float = 300, after_s: float = 600) -> TriggerWindow:
    return TriggerWindow(center - before_s, center + after_s)