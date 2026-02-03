import pandas as pd
from datetime import date, datetime

from dash import Dash, html, dcc, Input, Output
import dash_ag_grid as dag

from appdb import (
    getFundOverview,
    getDerivativesMetrics,
    getPositions,
    get_last_day_of_previous_month,
)
from dagrid  import create_grid

# ------------------------------------------------------------------------------
# Dash App Factory
# ------------------------------------------------------------------------------
def init_dash(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/",
        suppress_callback_exceptions=True,
    )
    # --------------------------------------------------------------------------
    # Layout (NO database calls here)
    # --------------------------------------------------------------------------
    dash_app.layout = html.Div(
        [
            # ---- Shared state ----
            dcc.Store(id="fund-overview-store"),
            html.H1("Zais Group Snowflake Data", style={"textAlign": "center"}),

            # ---- Controls ----
            html.Div(
                [
                    dcc.Dropdown(
                        id="filter-dropdown",
                        value="All",
                        style={"width": "300px"},
                    ),
                    dcc.DatePickerSingle(
                        id="asof-date",
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=date(2045, 12, 31),
                        date=get_last_day_of_previous_month(date.today()),
                        style={"marginLeft": "15px"},
                    ),
                ],
                style={"display": "flex", "marginBottom": "30px"},
            ),

            # ---- Grids ----
            html.H2("Fund Overview"),
            html.Div(id="fund-overview-grid"),

            html.H2("Fund Positions"),
            html.Div(id="fund-positions-grid"),

            html.H2("Fund Derivatives"),
            html.Div(id="fund-derivatives-grid"),
        ]
    )

    # --------------------------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------------------------

    # 1️⃣ Load Fund Overview ONCE (lazy, after app loads)
    @dash_app.callback(
        Output("fund-overview-store", "data"),
        Input("filter-dropdown", "value"),
    )
    def load_fund_overview(_):
        df = getFundOverview()
        return df.to_dict("records")

    # 2️⃣ Populate dropdown dynamically
    @dash_app.callback(
        Output("filter-dropdown", "options"),
        Input("fund-overview-store", "data"),
    )
    def update_dropdown(data):
        if not data:
            return [{"label": "All", "value": "All"}]

        df = pd.DataFrame(data)
        funds = sorted(df["fund_name"].unique())

        return (
            [{"label": "All", "value": "All"}]
            + [{"label": f, "value": f} for f in funds]
        )

    # 3️⃣ Fund Overview grid
    @dash_app.callback(
        Output("fund-overview-grid", "children"),
        Input("fund-overview-store", "data"),
        Input("filter-dropdown", "value"),
    )
    def update_fund_overview(data, selected_fund):
        if not data:
            return html.Div("No data available")

        df = pd.DataFrame(data)

        if selected_fund and selected_fund != "All":
            df = df[df["fund_name"] == selected_fund]

        return create_grid("FundOverview", df)

    # 4️⃣ Fund Positions grid
    @dash_app.callback(
        Output("fund-positions-grid", "children"),
        Input("asof-date", "date"),
        Input("filter-dropdown", "value"),
    )
    def update_positions(selected_date, selected_fund):
        if selected_date is None:
            selected_date = get_last_day_of_previous_month(date.today())

        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        df = getPositions(selected_date)
        if selected_fund and selected_fund != "All":
            if "fund_name" in df.columns:
                df = df[df["fund_name"] == selected_fund]

        return create_grid("FundPositions", df)

    # 5️⃣ Fund Derivatives grid
    @dash_app.callback(
        Output("fund-derivatives-grid", "children"),
        Input("asof-date", "date"),
        Input("filter-dropdown", "value"),
    )
    def update_derivatives(selected_date, selected_fund):
        if selected_date is None:
            selected_date = get_last_day_of_previous_month(date.today())

        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        df = getDerivativesMetrics(selected_date)
        return create_grid("FundDerivatives", df)

    return dash_app

