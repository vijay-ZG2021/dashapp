import pandas as pd
from appSqlDb import getFundOverview,getDerivativesMetrics,getPositions,get_last_day_of_previous_month
from dagrid import create_grid,create_pivot_grid
from dash import Dash,html,Input,Output,callback
import dash_ag_grid as dag
from dash import dcc
from datetime import date,datetime
from GridColumnFactory import GridSchema,GridColumnFactory
import dash

def init_dash(server):
    try:
        date_value=get_last_day_of_previous_month(date.today())
        dfFO = getFundOverview(date_value)
        dfDM = getDerivativesMetrics(date_value)
        dfPositions = getPositions(date_value)
    except ValueError:
       print(ValueError)
       
    app = dash.Dash(
        __name__,
        server=server,
        suppress_callback_exceptions=True,
        url_base_pathname='/dash/'  # Mount Dash here
    )
    app.layout = html.Div([
        html.H1("Zais Group Snowflake Data", style={'text-align': 'center'}),
        html.Div([
        html.Br(),
        html.Br(),
        dcc.Dropdown(
                    id='filter-dropdown',
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in dfFO['Fund_Name'].unique()],
                    value='All' ,
                    style={'height': '30px', 'width': '300px','marginTop':15,'marginBottom': 35}
                    ),
        dcc.DatePickerSingle(
            id='my-date-picker-single',
            min_date_allowed=date(2020, 1, 1),
            max_date_allowed=date(2045, 12, 31),
            initial_visible_month=date(2023, 4, 1),
            date=get_last_day_of_previous_month(date.today()),
            style={'height': '15px', 'width': '20px','marginTop': 25,'marginBottom': 25,'marginLeft': 10})],
            style={'display': 'flex', 'position':'relative', 'top':'8px','left':'56px'}
            ),
        html.P(''),
        dcc.Tabs(
            id="tabs-example-graph",
            value='tab-1-example-graph',
            parent_className = 'custom-tabs',
            className='custom-tabs-container',
            children=[
                dcc.Tab(
                label='Fund Performance',
                value='Tab-1',
                className='custom-tab',
                selected_className= 'custom-tab--selected'
                ),
                dcc.Tab(
                label='Derivatives',
                value='Tab-2',
                className='custom-tab',
                selected_className= 'custom-tab--selected'
                ),
                dcc.Tab(
                label='Positions Pivot',
                value='Tab-3',
                className='custom-tab',
                selected_className= 'custom-tab--selected'
                )
            ],
            style={'width': '50%','font-size': '18px'}
        ),
        html.Div(id='tabs-content-example-graph')
    ])

    @app.callback(
        Output('tabs-content-example-graph', 'children'),
        Input('tabs-example-graph','value'),
        Input('my-date-picker-single', 'date'),
        prevent_initial_call=True
    )

    def render_content(tab,date_value):
        if tab == 'Tab-1':  
            return html.Div([ 
                    html.Div(id='dd-output-container'),
                    create_grid("FundOverview",dfFO)
                ],style={'padding': 5, 'flex': 1})
        elif tab == 'Tab-2':
            return html.Div([
                html.H4(children = 'Fund Positions'),
                html.Label("Search   :    "),
                dcc.Input(id="search", placeholder="Search",value=''),
                create_grid("FundPositions",dfPositions),
                html.H4(children = 'Derivative Metrics'),
                create_grid("DerivativeMetrics",dfDM)
            ])
        elif tab == 'Tab-3':
            return html.Div([
                html.H4(children = 'Positions Pivot'),
                html.Div(id='pivot-table-container')
            ])

    #### Fund Overview 
    @callback(Output('FundOverview','dashGridOptions'), 
            Input('filter-dropdown','value'),     
            prevent_initial_call=True)

    def filter_overview(namevalue):
        fund_overview_options = {
            "isExternalFilterPresent": {"function": "true" if namevalue != 'All' else "false"},
            "doesExternalFilterPass": {"function": f"params.data.Fund_Name === '{namevalue}'" if namevalue != 'All' else "true"}}
        return fund_overview_options 

    @callback(Output('FundPositions','dashGridOptions'),
            [Input('search','value'),
            Input('my-date-picker-single', 'date')],
            prevent_initial_call=True)

    def positions(search_value,date_value):
        fund_positions_options = {
            "isExternalFilterPresent": {"function": "true" if search_value != '' else "false"}, 
            "doesExternalFilterPass": {"function": f"params.data.CUSIP === '{search_value}'" if (search_value != '') else "true"}}
        return fund_positions_options

    @app.callback( Output('pivot-table-container', 'children'),
                [Input("filter-dropdown", "value"),
                Input('my-date-picker-single', 'date')])

    def select_data( selected_data:str,date_value):
        date_value=get_last_day_of_previous_month(date.today())
        dfPositions= getPositions(date_value)
        if selected_data == 'All':
            filtered_df= dfPositions
        else :
            filtered_df = dfPositions[dfPositions['Fund_Name'] == selected_data]  
        pivot_grid = create_pivot_grid(
            "FundPositionsPivot",
            filtered_df,
            ["Fund_Name"],  # Rows to group by
            ["Product"],  # Pivoted columns
            ["marketValue"]  # Values to aggregate
        )
        return pivot_grid

