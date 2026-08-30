"""GAIA plane: a 2D PCA projection of alternatives and criteria.

The projection is built from the matrix of *unicriterion* net flows (each
alternative's net flow computed as if only one criterion mattered, weight
1). PCA (via SVD) of that matrix gives a 2D plane in which alternatives are
points and criteria are direction vectors; the resultant vector "pi" is the
weighted sum of the criteria vectors, showing the direction favored by the
current weighting.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
import pandas as pd

from promethee_core.core import compute_all_preference_matrices, compute_flows
from promethee_core.model import ProblemData


@dataclass
class GaiaResult:
    alternative_names: list[str]
    criterion_names: list[str]
    alternative_coords: np.ndarray  # (m, 2)
    criterion_coords: np.ndarray    # (n, 2)
    pi_vector: np.ndarray           # (2,) weighted resultant criterion vector
    quality: float                  # fraction of variance captured by the 2D plane (delta)


def compute_gaia(problem: ProblemData) -> GaiaResult:
    matrices = compute_all_preference_matrices(problem)
    criterion_names = list(matrices.keys())
    alt_names = [a.name for a in problem.active_alternatives()]
    if not criterion_names or not alt_names:
        raise ValueError("GAIA requires at least one active alternative and one active criterion.")

    unicriterion_flows = np.column_stack(
        [compute_flows(matrices[name])[2] for name in criterion_names]
    )  # shape (m, n)
    centered = unicriterion_flows - unicriterion_flows.mean(axis=0, keepdims=True)

    _, singular_values, vt = np.linalg.svd(centered, full_matrices=False)
    k = min(2, vt.shape[0])
    directions = vt[:k].T  # (n, k)
    alt_coords = centered @ directions  # (m, k)

    if k < 2:
        pad_cols = 2 - k
        alt_coords = np.hstack([alt_coords, np.zeros((alt_coords.shape[0], pad_cols))])
        directions = np.hstack([directions, np.zeros((directions.shape[0], pad_cols))])

    total_variance = float(np.sum(singular_values ** 2))
    quality = float(np.sum(singular_values[:2] ** 2) / total_variance) if total_variance > 0 else 0.0

    weights = problem.normalized_weights()
    weight_vector = np.array([weights[name] for name in criterion_names])
    pi_vector = weight_vector @ directions  # (2,)

    return GaiaResult(
        alternative_names=alt_names,
        criterion_names=criterion_names,
        alternative_coords=alt_coords,
        criterion_coords=directions,
        pi_vector=pi_vector,
        quality=quality,
    )


def export_gaia_to_excel(
    gaia: GaiaResult,
    alt_colors: dict[str, str],
    crit_colors: dict[str, str],
    weights: dict[str, float],
) -> bytes:
    """Export the GAIA plane's exact coordinates to Excel."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(
            {
                "alternative": gaia.alternative_names,
                "PC1": gaia.alternative_coords[:, 0],
                "PC2": gaia.alternative_coords[:, 1],
                "color": [alt_colors.get(n, "") for n in gaia.alternative_names],
            }
        ).to_excel(writer, sheet_name="Alternatives", index=False)

        pd.DataFrame(
            {
                "criterion": gaia.criterion_names,
                "PC1": gaia.criterion_coords[:, 0],
                "PC2": gaia.criterion_coords[:, 1],
                "normalized_weight": [weights.get(n, 0.0) for n in gaia.criterion_names],
                "color": [crit_colors.get(n, "") for n in gaia.criterion_names],
            }
        ).to_excel(writer, sheet_name="Criteria", index=False)

        pd.DataFrame(
            {
                "PC1": [gaia.pi_vector[0]],
                "PC2": [gaia.pi_vector[1]],
                "plane_quality": [gaia.quality],
            }
        ).to_excel(writer, sheet_name="Pi vector", index=False)

    return buffer.getvalue()
