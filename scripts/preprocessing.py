"""
Lightweight preprocessing helpers used by tests and quick local workflows.

This is intentionally minimal and does NOT require access to full MIMIC datasets.
"""

from __future__ import annotations

import pandas as pd


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning for a dataframe containing an `age_at_admission` column.

    - Ensures `age_at_admission` is numeric
    - Drops rows with missing ages
    - Filters to adult ages [18, 120]
    """
    if "age_at_admission" not in df.columns:
        raise ValueError("Missing required column: age_at_admission")

    out = df.copy()
    out["age_at_admission"] = pd.to_numeric(out["age_at_admission"], errors="coerce")
    out = out.dropna(subset=["age_at_admission"])
    out = out[(out["age_at_admission"] >= 18) & (out["age_at_admission"] <= 120)]
    return out.reset_index(drop=True)
