"""Weight stability-interval sensitivity analysis.

When a single criterion's weight w is varied while every other active
criterion's weight is rescaled proportionally (so the total still sums to
1), the net flow of every alternative turns out to be an *affine* function
of w:

    Phi(A_i; w) = (1 - w) * C_i + w * D_i

where ``D_i`` is the alternative's unicriterion net flow using only the
criterion under study (w=1 case), and ``C_i`` is the net flow that would
result from dropping that criterion entirely and renormalizing the rest
(w=0 case). This module derives C_i and D_i from already-computed
PROMETHEE results.

The top-x sequence (positions 1..x, in order) stays unchanged exactly as
long as every alternative currently in the top-x beats every other
alternative it must beat: the other top-x members (internal order) and
every alternative outside the top-x (the cut). Each such pair is an affine
vs. affine comparison with at most one crossing point, so the stability
interval is the intersection of all of these half-line constraints - i.e.
we must check each top-x member against *every* other alternative, not
just the ones adjacent to it in the current ranking. Checking only
adjacent ranks misses cascades: a lower-ranked alternative can leapfrog
into the lead by first overtaking an intermediate rank, and that
intermediate crossing happens before the leader is ever directly
challenged by its immediate neighbour.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from promethee_core.core import PrometheeResult, compute_flows


def _crossing(C_i: float, D_i: float, C_j: float, D_j: float) -> float | None:
    """Weight w at which two alternatives' affine flow lines intersect, or None if parallel."""
    denom = (D_i - C_i) - (D_j - C_j)
    if abs(denom) < 1e-12:
        return None
    return (C_j - C_i) / denom


@dataclass
class WeightSensitivity:
    alt_names: list[str]
    C: np.ndarray  # net flow at w=0 (criterion dropped, rest renormalized)
    D: np.ndarray  # net flow at w=1 (unicriterion flow for this criterion alone)
    w0: float      # the criterion's current normalized weight
    criterion_name: str

    def flow_at(self, w) -> np.ndarray:
        """Net flow of every alternative at hypothetical weight(s) w. w may be scalar or array."""
        w = np.asarray(w, dtype=float)
        return (1 - w)[..., None] * self.C + w[..., None] * self.D

    def stability_interval(self, top_x: int) -> tuple[float, float, list[dict]]:
        """Widest [w_low, w_high] around w0 that keeps the top-x ranking sequence unchanged."""
        m = len(self.alt_names)
        top_x = max(1, min(top_x, m))

        f0 = self.flow_at(np.array(self.w0))
        order = np.argsort(f0)[::-1]  # alternative indices, best first, at the current weight
        top_indices = order[:top_x]

        low_candidates: list[float] = []
        high_candidates: list[float] = []
        crossings: list[dict] = []
        seen_pairs: set[tuple[int, int]] = set()
        for i in top_indices:
            for j in range(m):
                if j == i:
                    continue
                pair = (min(i, j), max(i, j))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                w_cross = _crossing(self.C[i], self.D[i], self.C[j], self.D[j])
                if w_cross is None or not (0.0 <= w_cross <= 1.0):
                    continue
                crossings.append({"a": self.alt_names[i], "b": self.alt_names[j], "w": w_cross})
                if w_cross <= self.w0:
                    low_candidates.append(w_cross)
                if w_cross >= self.w0:
                    high_candidates.append(w_cross)

        w_low = max(low_candidates) if low_candidates else 0.0
        w_high = min(high_candidates) if high_candidates else 1.0
        return w_low, w_high, crossings


def compute_weight_sensitivity(result: PrometheeResult, criterion_name: str) -> WeightSensitivity:
    """Build the weight-sensitivity model for one criterion from a computed PROMETHEE result."""
    weights = result.weights
    if criterion_name not in weights:
        raise KeyError(f"Unknown or inactive criterion: {criterion_name}")
    if len(weights) < 2:
        raise ValueError("Sensitivity analysis needs at least two active criteria.")

    w0 = weights[criterion_name]
    if w0 >= 1.0 - 1e-9:
        raise ValueError(
            "This criterion currently holds all the weight; there is no other active "
            "criterion to rescale, so a stability interval cannot be computed."
        )

    P_k0 = result.criterion_matrices[criterion_name]
    _, _, D = compute_flows(P_k0)
    C = (result.phi_net - w0 * D) / (1.0 - w0)
    return WeightSensitivity(
        alt_names=result.alternative_names, C=C, D=D, w0=w0, criterion_name=criterion_name
    )
