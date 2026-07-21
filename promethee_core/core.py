"""Core PROMETHEE computations: preference matrices, aggregation, and flows."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from promethee_core.model import Criterion, Direction, ProblemData
from promethee_core.preference_functions import compute_preference


def preference_matrix_for_criterion(values: pd.Series, criterion: Criterion) -> np.ndarray:
    """Build the m x m unicriterion preference matrix P_k for one criterion.

    ``P[i, j]`` is how much alternative i is preferred to alternative j
    according to this criterion alone.
    """
    v = values.to_numpy(dtype=float)
    m = len(v)
    sign = 1.0 if criterion.direction == Direction.MAX else -1.0
    P = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            d = sign * (v[i] - v[j])
            P[i, j] = compute_preference(
                d, criterion.preference_function, q=criterion.q, p=criterion.p, s=criterion.s
            )
    return P


def compute_all_preference_matrices(problem: ProblemData) -> dict[str, np.ndarray]:
    """Return {criterion_name: P_k} for every active criterion, over active alternatives."""
    values = problem.active_values()
    return {
        criterion.name: preference_matrix_for_criterion(values[criterion.name], criterion)
        for criterion in problem.active_criteria()
    }


def aggregate_preference_matrix(
    matrices: dict[str, np.ndarray], weights: dict[str, float]
) -> np.ndarray:
    """Weighted sum P = sum_k w_k * P_k."""
    names = list(matrices.keys())
    if not names:
        return np.zeros((0, 0))
    total = np.zeros_like(matrices[names[0]])
    for name in names:
        total = total + weights[name] * matrices[name]
    return total


def compute_flows(P: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Positive, negative and net outranking flows from an aggregated preference matrix."""
    m = P.shape[0]
    if m <= 1:
        empty = np.zeros(m)
        return empty, empty, empty
    phi_plus = P.sum(axis=1) / (m - 1)
    phi_minus = P.sum(axis=0) / (m - 1)
    phi_net = phi_plus - phi_minus
    return phi_plus, phi_minus, phi_net


def rank_by(alt_names: list[str], scores: np.ndarray, descending: bool = True) -> list[str]:
    """Alternative names ordered by score (best first when descending)."""
    order = np.argsort(scores, kind="stable")
    if descending:
        order = order[::-1]
    return [alt_names[i] for i in order]


@dataclass
class PrometheeResult:
    alternative_names: list[str]
    criterion_matrices: dict[str, np.ndarray]
    weights: dict[str, float]
    aggregated_matrix: np.ndarray
    phi_plus: np.ndarray
    phi_minus: np.ndarray
    phi_net: np.ndarray

    @property
    def ranking_positive(self) -> list[str]:
        return rank_by(self.alternative_names, self.phi_plus, descending=True)

    @property
    def ranking_negative(self) -> list[str]:
        return rank_by(self.alternative_names, self.phi_minus, descending=False)

    @property
    def ranking_net(self) -> list[str]:
        return rank_by(self.alternative_names, self.phi_net, descending=True)


def compute_promethee(problem: ProblemData) -> PrometheeResult:
    """Run the full PROMETHEE computation for the currently active problem."""
    alt_names = [a.name for a in problem.active_alternatives()]
    weights = problem.normalized_weights()
    matrices = compute_all_preference_matrices(problem)
    P = aggregate_preference_matrix(matrices, weights)
    phi_plus, phi_minus, phi_net = compute_flows(P)
    return PrometheeResult(
        alternative_names=alt_names,
        criterion_matrices=matrices,
        weights=weights,
        aggregated_matrix=P,
        phi_plus=phi_plus,
        phi_minus=phi_minus,
        phi_net=phi_net,
    )
