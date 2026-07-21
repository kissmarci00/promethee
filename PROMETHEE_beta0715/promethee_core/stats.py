"""Descriptive statistics over the raw decision-matrix data."""
from __future__ import annotations

import pandas as pd


def summarize(values: pd.DataFrame) -> pd.DataFrame:
    """Per-criterion mean/min/max/standard deviation, one row per statistic."""
    return pd.DataFrame(
        {
            "mean": values.mean(),
            "min": values.min(),
            "max": values.max(),
            "std": values.std(ddof=0),
        }
    ).T
