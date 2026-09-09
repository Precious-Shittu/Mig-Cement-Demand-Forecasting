import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import clean, model_results, sim_results, wmape, BEST_MODEL_COL, BEST_MODEL_NAME, TEST_START, TEST_END

dash.register_page(__name__, path="/", name="Overview")


def kpi_card(label: str, value: str, sub: str = "", color: str = "#2b6cb0"):
    return html.Div([
        html.Div(label, style={"fontSize": "13px", "color": "#718096", "marginBottom": "4px"}),
        html.Div(value, style={"fontSize": "28px", "fontWeight": "700", "color": color}),
        html.Div(sub, style={"fontSize": "12px", "color": "#a0aec0", "marginTop": "4px"}),
    ], style={
        "backgroundColor": "white", "borderRadius": "8px", "padding": "16px 20px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "flex": "1", "minWidth": "200px",
    })


# ---- Compute headline KPIs ----
model_wmape = wmape(model_results["actual"], model_results[BEST_MODEL_COL])

hist_stockout = sim_results["stockout_at_pour"].mean()
sim_stockout = sim_results["simulated_stockout"].mean()

cons = sim_results[sim_results["behavior"] == "conservative"]
first_day, last_day = cons["date"].min(), cons["date"].max()
hist_overflow_change = (
    cons[cons["date"] == last_day]["overflow_tonnes"].sum()
    - cons[cons["date"] == first_day]["overflow_tonnes"].sum()
)
sim_overflow_change = (
    cons[cons["date"] == last_day]["simulated_overflow_tonnes"].sum()
    - cons[cons["date"] == first_day]["simulated_overflow_tonnes"].sum()
)

# ---- Network-level forecast vs actual chart ----
network_daily = model_results.groupby("date").agg(
    actual=("actual", "sum"),
    forecast=(BEST_MODEL_COL, "sum"),
).reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=network_daily["date"], y=network_daily["actual"], name="Actual", line=dict(color="#1a365d", width=2)))
fig.add_trace(go.Scatter(x=network_daily["date"], y=network_daily["forecast"], name=f"Forecast ({BEST_MODEL_NAME})", line=dict(color="#38a169", width=2, dash="dash")))
fig.update_layout(
    title="Network-wide daily cement consumption — actual vs forecast (8-week test window)",
    xaxis_title="Date", yaxis_title="Tonnes",
    template="plotly_white", height=420, margin=dict(t=60, l=40, r=20, b=40),
)

layout = html.Div([
    html.H2("Network Overview", style={"marginBottom": "4px"}),
    html.P(
        f"Test window: {TEST_START.date()} to {TEST_END.date()} · {clean['site_id'].nunique()} sites",
        style={"color": "#718096", "marginTop": "0"},
    ),

    html.Div([
        kpi_card("Forecast Accuracy (WMAPE)", f"{model_wmape:.1f}%", f"{BEST_MODEL_NAME} · target ≤15%",
                 color="#38a169" if model_wmape <= 15 else "#dd6b20"),
        kpi_card("Stockout Rate", f"{sim_stockout:.1%}", f"vs {hist_stockout:.1%} historically",
                 color="#38a169"),
        kpi_card("Conservative-Site Overflow Trend", f"{sim_overflow_change:+,.0f}t",
                 f"vs {hist_overflow_change:+,.0f}t historically (56-day change)",
                 color="#38a169" if sim_overflow_change < hist_overflow_change else "#dd6b20"),
        kpi_card("Sites Monitored", f"{clean['site_id'].nunique()}",
                 f"{clean['region'].nunique()} regions"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

    dcc.Graph(figure=fig),

    html.P(
        "Forecasting model selected after comparing four candidates (seasonal-naive, SARIMAX, "
        "Random Forest, Gradient Boosting) on a genuine 56-day recursive forecast — see the "
        "Site Forecast page for per-site detail, or the Reorder Alerts page for current "
        "inventory status.",
        style={"color": "#718096", "fontSize": "13px", "marginTop": "16px"},
    ),
])
