import dash
from dash import html, dcc, dash_table, callback, Input, Output
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import sim_results, reorder_points, clean, BEHAVIORS

dash.register_page(__name__, path="/alerts", name="Reorder Alerts")

# Latest simulated on-hand per site (last day of the simulation window)
latest_date = sim_results["date"].max()
latest_status = sim_results[sim_results["date"] == latest_date][
    ["site_id", "simulated_on_hand", "simulated_stockout", "simulated_over_capacity"]
]

site_regions = clean[["site_id", "region"]].drop_duplicates("site_id")

alerts_df = reorder_points.merge(latest_status, on="site_id").merge(site_regions, on="site_id")
alerts_df["status"] = alerts_df.apply(
    lambda r: "REORDER NOW" if r["simulated_on_hand"] < r["reorder_point"] else "OK", axis=1
)
alerts_df = alerts_df[[
    "site_id", "behavior", "region", "silo_capacity",
    "simulated_on_hand", "reorder_point", "order_up_to_level", "status",
]].round(1).sort_values("status", ascending=False)

layout = html.Div([
    html.H2("Reorder Alerts", style={"marginBottom": "4px"}),
    html.P(
        f"Current simulated inventory position vs. reorder point, as of {latest_date.date()} "
        "(last day of the simulation window).",
        style={"color": "#718096", "marginTop": "0"},
    ),

    html.Div([
        html.Label("Filter by behaviour", style={"fontWeight": "600", "marginRight": "8px"}),
        dcc.Dropdown(
            id="behavior-filter",
            options=[{"label": "All", "value": "All"}] + [{"label": b.capitalize(), "value": b} for b in BEHAVIORS],
            value="All", clearable=False, style={"width": "240px"},
        ),
    ], style={"marginBottom": "20px"}),

    dash_table.DataTable(
        id="alerts-table",
        columns=[
            {"name": "Site", "id": "site_id"},
            {"name": "Behaviour", "id": "behavior"},
            {"name": "Region", "id": "region"},
            {"name": "Silo Capacity (t)", "id": "silo_capacity"},
            {"name": "Current On-Hand (t)", "id": "simulated_on_hand"},
            {"name": "Reorder Point (t)", "id": "reorder_point"},
            {"name": "Order-Up-To (t)", "id": "order_up_to_level"},
            {"name": "Status", "id": "status"},
        ],
        data=alerts_df.to_dict("records"),
        style_cell={"padding": "10px", "fontFamily": "Segoe UI, Arial, sans-serif", "fontSize": "13px"},
        style_header={"backgroundColor": "#1a365d", "color": "white", "fontWeight": "600"},
        style_data_conditional=[
            {
                "if": {"filter_query": '{status} = "REORDER NOW"'},
                "backgroundColor": "#fff5f5", "color": "#c53030", "fontWeight": "600",
            },
        ],
        sort_action="native",
        page_size=15,
    ),
])


@callback(Output("alerts-table", "data"), Input("behavior-filter", "value"))
def filter_table(behavior):
    if behavior == "All":
        return alerts_df.to_dict("records")
    return alerts_df[alerts_df["behavior"] == behavior].to_dict("records")
