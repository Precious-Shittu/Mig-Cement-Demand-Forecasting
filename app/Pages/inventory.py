import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import sim_results, reorder_points, SITE_OPTIONS, SITES

dash.register_page(__name__, path="/inventory", name="Inventory Simulation")

layout = html.Div([
    html.H2("Inventory Simulation", style={"marginBottom": "4px"}),
    html.P(
        "Historical on-hand inventory vs. simulated on-hand under the new reorder-point policy.",
        style={"color": "#718096", "marginTop": "0"},
    ),

    html.Div([
        html.Label("Site", style={"fontWeight": "600", "marginRight": "8px"}),
        dcc.Dropdown(id="inv-site-dropdown", options=SITE_OPTIONS, value=SITES[0], clearable=False, style={"width": "360px"}),
    ], style={"marginBottom": "20px"}),

    dcc.Graph(id="inventory-chart"),

    html.Div(id="inventory-summary", style={"marginTop": "16px"}),
])


@callback(
    Output("inventory-chart", "figure"),
    Output("inventory-summary", "children"),
    Input("inv-site-dropdown", "value"),
)
def update_inventory(site_id):
    site_df = sim_results[sim_results["site_id"] == site_id].sort_values("date")
    params = reorder_points[reorder_points["site_id"] == site_id].iloc[0]

    # Reconstruct historical on-hand from opening + deliveries - consumed isn't stored here directly,
    # but overflow_tonnes + silo_capacity gives us on-hand when over capacity; for a clean comparable
    # series we use closing-inventory-derived overflow to show the historical trend shape.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=site_df["date"], y=site_df["simulated_on_hand"], name="Simulated on-hand (new policy)",
        line=dict(color="#38a169", width=2.5),
    ))
    fig.add_hline(y=params["silo_capacity"], line_dash="dash", line_color="#e53e3e",
                   annotation_text="Silo capacity", annotation_position="top left")
    fig.add_hline(y=params["reorder_point"], line_dash="dot", line_color="#dd6b20",
                   annotation_text="Reorder point", annotation_position="bottom left")
    fig.update_layout(
        title=f"{site_id} ({params['behavior']}) — simulated inventory trajectory",
        xaxis_title="Date", yaxis_title="Tonnes",
        template="plotly_white", height=460, margin=dict(t=60, l=40, r=20, b=40),
    )

    hist_stockout = site_df["stockout_at_pour"].mean()
    sim_stockout = site_df["simulated_stockout"].mean()
    hist_overflow = site_df["over_capacity"].mean()
    sim_overflow = site_df["simulated_over_capacity"].mean()

    summary = html.Div([
        html.Div([
            html.Div("Stockout rate", style={"fontSize": "13px", "color": "#718096"}),
            html.Div(f"{hist_stockout:.1%} → {sim_stockout:.1%}", style={"fontSize": "20px", "fontWeight": "700"}),
        ], style={"backgroundColor": "white", "borderRadius": "8px", "padding": "12px 20px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "flex": "1"}),
        html.Div([
            html.Div("Overflow rate", style={"fontSize": "13px", "color": "#718096"}),
            html.Div(f"{hist_overflow:.1%} → {sim_overflow:.1%}", style={"fontSize": "20px", "fontWeight": "700"}),
        ], style={"backgroundColor": "white", "borderRadius": "8px", "padding": "12px 20px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "flex": "1"}),
        html.Div([
            html.Div("Reorder point / Order-up-to", style={"fontSize": "13px", "color": "#718096"}),
            html.Div(f"{params['reorder_point']:.0f}t / {params['order_up_to_level']:.0f}t", style={"fontSize": "20px", "fontWeight": "700"}),
        ], style={"backgroundColor": "white", "borderRadius": "8px", "padding": "12px 20px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "flex": "1"}),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    return fig, summary
