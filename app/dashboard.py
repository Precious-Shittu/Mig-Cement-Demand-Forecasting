"""
MIG Cement Demand Forecasting — Dashboard
Multi-page Plotly Dash app: forecasts, inventory simulation, and reorder alerts by site.

Run with:  python dashboard.py
Then open: http://127.0.0.1:8050
"""

import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = "MIG Cement Demand Dashboard"

NAV_STYLE = {
    "padding": "12px 24px",
    "borderBottom": "1px solid #e2e8f0",
    "display": "flex",
    "gap": "24px",
    "alignItems": "center",
    "backgroundColor": "#1a365d",
}

LINK_STYLE = {
    "color": "#e2e8f0",
    "textDecoration": "none",
    "fontWeight": "500",
}

app.layout = html.Div([
    html.Div([
        html.Span("MIG Cement Demand Dashboard", style={"color": "white", "fontWeight": "700", "fontSize": "18px", "marginRight": "16px"}),
        *[
            dcc.Link(page["name"], href=page["path"], style=LINK_STYLE)
            for page in dash.page_registry.values()
        ],
    ], style=NAV_STYLE),
    html.Div(dash.page_container, style={"padding": "24px", "maxWidth": "1200px", "margin": "0 auto"}),
], style={"fontFamily": "Segoe UI, Arial, sans-serif", "backgroundColor": "#f7fafc", "minHeight": "100vh"})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
