import dash_ag_grid as dag
from datetime import datetime
from GridColumnFactory import GridSchema,GridColumnFactory
import pandas as pd

textFilterParams = {
    "filterOptions" : ["contains","notContains"],
    "debounceMe":200,
    "maxNumConditions" : 1,
}
def currency_format(value: str) -> str:
    try:
        return f"${float(value):,.2f}"
    except ValueError:
        return value

def double_format(value: str) -> str:
    try:
        return f"{float(value):,.2f}"
    except ValueError:
        return value

def millions_format(value : str)-> str:
    try:
        if value:
            return f"${value / 1_000_000:,.2f}M"
        else:
            return "-"
    except ValueError:
        return value

def date_format(value: str)-> str:
    try:
        return "{:.2f}M".format(value)
    except ValueError:
        return value

def format_percent(value, decimals=2):
    if value is None:
        return "-"
    return f"{value / 1_00 :.{decimals}%}"

def create_schema(gridId:str):
    schema = GridSchema()
    if gridId == "FundOverview":
        #taFrame
##Columns: [id, asof, deriv_id, security_name, beta, yield, spread, effective_duration, spread_duration, soft_reserves, delta, dv01, aggregate_id, version]
        schema.add_column(GridColumnFactory.create("fund_name","Fund Name", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("gav_in_fund_ccy","GAV(mm)", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("total_leverage","LEVERAGE", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("margin_posted_fund_ccy","MARGIN POSTED", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("cash_net_of_reserves_as_pct_of_gav","Cash % of GAV(%)", filter=True,editable=True,valueFormatter= format_percent))
    
    if gridId=="FundDerivatives" :
        #schema.add_column(GridColumnFactory.create("SECURITY_NAME","Description", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("asof","As Of Date", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("beta","BETA", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("yield","YIELD", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("spread","SPREAD", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("deriv_id","DERIV_ID", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("spread_duration","SPREAD_DURATION", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("dv01","DV01", filter=True,editable=True,valueFormatter= double_format)) 
    if gridId=="FundPositions" :
        schema.add_column(GridColumnFactory.create("fund_name","Fund Name", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("description","Description", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("as_of_date","Date (yyyy-mm-dd)", filter=True))
        schema.add_column(GridColumnFactory.create("original_notional","Original Notional", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("fund_currency","Currency", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("current_notional","Current Notional", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("val","Market Value", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("price","Price", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("product","Product", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("class","SubClass", filter=True,editable=True ))  
    return schema


def get_col_defs(gridId:str,dfData):
    schema = create_schema(gridId)
    colDefs = schema.get_columns_array()
    return colDefs

def get_formatted_data(gridId : str, dfData) :  
    schema = create_schema(gridId)
    arrayObj =schema.get_columns_arrayObj()
    # Now you can create a new DataFrame using its columns:
    formatted_df = pd.DataFrame(columns=dfData.columns)
    for index, row in dfData.iterrows():
        formatted_row = {
            col.field: col.format_value(row[col.field]) for name,col in arrayObj
        }
        formatted_df= pd.concat([formatted_df, pd.DataFrame([formatted_row])], ignore_index=True)
    return formatted_df

def create_grid(gridId:str,dfData):
    """
        Creates a Dash Ag Grid 

        Args: 
        DataFrame : Input data frame to display in the grid
        colDefs :  Details of Column Name, Label, Filters etc.
        
        Returns : 
            returns an AG Grid
    """
    colDefs = get_col_defs(gridId,dfData)
    formatted_df= get_formatted_data(gridId,dfData)

    grid =  dag.AgGrid(
        id=gridId,
        rowData=formatted_df.to_dict("records"),
        columnDefs=colDefs,
        defaultColDef = {"flex":1, "minWidth":150, "floatingFilter":True},
        columnSize = "sizeToFit",
        style={"height": "500px", "width": "100%"},
        dashGridOptions={
            'animateRows':False,
            'pagination':True,
            "suppressAggFuncInHeader": True,
        }
    )
    return grid