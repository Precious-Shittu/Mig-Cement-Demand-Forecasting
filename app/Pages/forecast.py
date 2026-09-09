import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import model_results, SITE_OPTIONS, SITES, MODEL_LABELS, wmape

dash.register_page(__name__, path="/forecast", name="Site Forecast")

MODEL_COLORS = {
    "forecast_naive": "#a0aec0",
    "forecast_sarimax": "#dd6b20",
    "forecast_rf": "#805ad5",
    "forecast_tuned_rf": "#38a169",
}

layout = html.Div([
    html.H2("Site Forecast", style={"marginBottom": "4px"}),
    html.P("8-week forecast vs actual consumption, by site and model.", style={"color": "#718096", "marginTop": "0"}),

    html.Div([
        html.Label("Site", style={"fontWeight": "600", "marginRight": "8px"}),
        dcc.Dropdown(id="site-dropdown", options=SITE_OPTIONS, value=SITES[0], clearable=False, style={"width": "360px"}),
    ], style={"marginBottom": "20px"}),

    dcc.Graph(id="forecast-chart"),

    html.Div(id="site-wmape-table", style={"marginTop": "16px"}),
])


@callback(Output("forecast-chart", "figure"), Input("site-dropdown", "value"))
def update_chart(site_id):
    site_df = model_results[model_results["site_id"] == site_id].sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=site_df["date"], y=site_df["actual"], name="Actual",
        line=dict(color="#1a365d", width=2.5), mode="lines+markers", marker=dict(size=4),
    ))
    for col, label in MODEL_LABELS.items():
        fig.add_trace(go.Scatter(
            x=site_df["date"], y=site_df[col], name=label,
            line=dict(color=MODEL_COLORS[col], width=1.5, dash="dash"),
        ))
    fig.update_layout(
        title=f"{site_id} — 8-week forecast vs actual",
        xaxis_title="Date", yaxis_title="Tonnes",
        template="plotly_white", height=460, margin=dict(t=60, l=40, r=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


@callback(Output("site-wmape-table", "children"), Input("site-dropdown", "value"))
def update_wmape_table(site_id):
    site_df = model_results[model_results["site_id"] == site_id]
    rows = []
    for col, label in MODEL_LABELS.items():
        score = wmape(site_df["actual"], site_df[col])
        rows.append(html.Tr([
            html.Td(label, style={"padding": "6px 12px"}),
            html.Td(f"{score:.1f}%", style={"padding": "6px 12px", "textAlign": "right", "fontWeight": "600"}),
        ]))
    return html.Table(
        [html.Thead(html.Tr([html.Th("Model", style={"padding": "6px 12px", "textAlign": "left"}), html.Th("WMAPE (this site)", style={"padding": "6px 12px", "textAlign": "right"})]))] + [html.Tbody(rows)],
        style={"backgroundColor": "white", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "borderCollapse": "collapse", "width": "100%", "maxWidth": "420px"},
    )
