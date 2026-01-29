import pandas as pd
from appdb import getFundOverview,getDerivativesMetrics,getPositions,get_last_day_of_previous_month
from dagrid import create_grid 
from dash import Dash,html,Input,Output,callback
import dash_ag_grid as dag
from dash import dcc
from datetime import date,datetime
#from GridColumnFactory import GridSchema,GridColumnFactory
import dash

def init_dash(server):
    try:
        date_value=get_last_day_of_previous_month(date.today())
        dfFO = getFundOverview()
        dfDM = getDerivativesMetrics(date_value)
        dfPositions = getPositions(date_value)
    except ValueError:
       print(ValueError)
       
    dash_app = dash.Dash(
        __name__,
        server=server,
        suppress_callback_exceptions=True,
        url_base_pathname='/dash/'  # Mount Dash here
    )
    dash_app.layout = html.Div([
        html.H1("Zais Group Snowflake Data", style={'text-align': 'center'}),
        html.Div([
        html.Br(),
        html.Br(),
        dcc.Dropdown(
                    id='filter-dropdown',
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in dfFO['FUND_NAME'].unique()],
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
        html.H2("Fund Overview", style={'text-align': 'left'}),
        html.Div(id='fund-overview-grid'),
        html.P(''),
        html.H2("Fund Positions", style={'text-align': 'left'}),
        html.Div(id='fund-positions-grid'),
        html.P(''),
        html.H2("Fund Derivatives", style={'text-align': 'left'}),
        html.Div(id='fund-derivatives-grid'),
         ])
    
    #callback for Fund Overview grid
    @dash_app.callback(
        Output('fund-overview-grid','children'),
        Input('filter-dropdown','value')
    )
    def update_fund_overview(selected_fund):
        dfFO= getFundOverview()
        if selected_fund and selected_fund!='All':
            dfFO = dfFO[dfFO['FUND_NAME']== selected_fund]
        
        return create_grid("FundOverview",dfFO)
    
    #callback for Fund Positions Grid
    @dash_app.callback(
        Output('fund-positions-grid','children'),
        Input('my-date-picker-single','date'),
        Input('filter-dropdown','value')
    )
    def update_fund_positions(selected_date,selected_fund):
        if selected_date is None:
            selected_date= get_last_day_of_previous_month(date.today())
        if isinstance(selected_date,str):
            selected_date=datetime.strptime(selected_date, '%Y-%m-%d').date()
        dfPositions = getPositions(selected_date)

        return create_grid("FundPositions",dfPositions)

     # Callback for Fund Derivatives grid
    @dash_app.callback(
        Output('fund-derivatives-grid', 'children'),
        Input('my-date-picker-single', 'date'),
        Input('filter-dropdown', 'value')
    )
    def update_fund_derivatives(selected_date, selected_fund):
        if selected_date is None:
            selected_date = get_last_day_of_previous_month(date.today())
        
        # Convert string date to date object if needed
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        dfDM = getDerivativesMetrics(selected_date)
        
        if selected_fund and selected_fund != 'All':
            # Adjust column name based on your actual dataframe structure
            if 'FUND_NAME' in dfDM.columns:
                dfDM = dfDM[dfDM['FUND_NAME'] == selected_fund]
        
        return create_grid("FundDerivatives", dfDM)

    return dash_app

