"""
Lightweight data validation used by tests and quick checks.

Produces a small CSV report with per-column missing counts and basic numeric stats.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


def validate_data(input_csv: Union[str, Path], report_path: Union[str, Path]) -> None:
  input_csv = Path(input_csv)
  report_path = Path(report_path)

  df = pd.read_csv(input_csv)

  rows = []
  for col in df.columns:
    s = df[col]
    row = {
      "column": col,
      "missing_values": int(s.isna().sum()),
      "dtype": str(s.dtype),
    }
    if pd.api.types.is_numeric_dtype(s):
      row.update(
        {
          "mean": float(s.mean()) if len(s.dropna()) else None,
          "min": float(s.min()) if len(s.dropna()) else None,
          "max": float(s.max()) if len(s.dropna()) else None,
        }
      )
    rows.append(row)

  report_df = pd.DataFrame(rows)
  report_path.parent.mkdir(parents=True, exist_ok=True)
  report_df.to_csv(report_path, index=False)



