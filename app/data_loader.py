"""
Shared data loading for the MIG Cement Demand Forecasting dashboard.
Loads all pre-computed outputs from the pipeline notebooks once, at app startup,
so every page can import from here instead of re-reading files.
"""

import pandas as pd
from pathlib import Path

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

clean = pd.read_parquet(OUTPUTS_DIR / "cement_demand_clean.parquet")
model_results = pd.read_parquet(OUTPUTS_DIR / "model_comparison_results_tuned.parquet")
reorder_points = pd.read_parquet(OUTPUTS_DIR / "reorder_point_framework.parquet").reset_index()
sim_results = pd.read_parquet(OUTPUTS_DIR / "inventory_simulation_results.parquet")

SITES = sorted(clean["site_id"].unique())
BEHAVIORS = sorted(clean["behavior"].unique())
REGIONS = sorted(clean["region"].unique())

TEST_START = model_results["date"].min()
TEST_END = model_results["date"].max()

MODEL_LABELS = {
    "forecast_naive": "Seasonal-Naive",
    "forecast_sarimax": "SARIMAX",
    "forecast_rf": "Random Forest (original)",
    "forecast_tuned_rf": "Random Forest (tuned)",
}

BEST_MODEL_COL = "forecast_tuned_rf"
BEST_MODEL_NAME = "Random Forest (tuned)"


def wmape(actual: pd.Series, pred: pd.Series) -> float:
    return (abs(actual - pred).sum() / abs(actual).sum()) * 100


def site_label(site_id: str) -> str:
    """Site dropdown label, e.g. 'SITE_002 (conservative, South)'."""
    row = clean[clean["site_id"] == site_id].iloc[0]
    return f"{site_id} ({row['behavior']}, {row['region']})"


SITE_OPTIONS = [{"label": site_label(s), "value": s} for s in SITES]
