from dataclasses import dataclass

import numpy as np


@dataclass
class Schedule:
    start: float
    end: float
    steps: int
    kind: str = "exp"   # "exp" | "linear" | "cosine"

    def __call__(self, t):
        x = min(max(t / self.steps, 0.0), 1.0)
        if self.kind == "linear":
            f = x
        elif self.kind == "cosine":
            f = 0.5 * (1 - np.cos(np.pi * x))
        else:  # exp, reaches ~95% of the way at x=1
            f = 1 - np.exp(-3 * x)
        return self.start + (self.end - self.start) * f