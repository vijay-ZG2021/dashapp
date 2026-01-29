import dash_ag_grid as dag
import dash_pivottable
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
        schema.add_column(GridColumnFactory.create("FUND_NAME","Fund Name", filter=True,editable=True))
       # schema.add_column(GridColumnFactory.create("AsOfDate","Date (yyyy-mm-dd)", filter=True,editable=True))
        #schema.add_column(GridColumnFactory.create("Type","Type", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("GAV_IN_FUND_CCY","GAV(mm)", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("TOTAL_LEVERAGE","LEVERAGE", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("MARGIN_POSTED_FUND_CCY","MARGIN POSTED", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("CASH_NET_OF_RESERVES_AS_PCT_OF_GAV","Cash % of GAV(%)", filter=True,editable=True,valueFormatter= format_percent))
    
    if gridId=="FundDerivatives" :
        schema.add_column(GridColumnFactory.create("SECURITY_NAME","Description", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("ASOF","As Of Date", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("BETA","BETA", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("YIELD","YIELD", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("SPREAD","SPREAD", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("DERIV_ID","DERIV_ID", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("SPREAD_DURATION","SPREAD_DURATION", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("DV01","DV01", filter=True,editable=True,valueFormatter= double_format)) 
    if gridId=="FundPositions" :
        schema.add_column(GridColumnFactory.create("FUND_NAME","Fund Name", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("DESCRIPTION","Description", filter=True,editable=True))
        schema.add_column(GridColumnFactory.create("AS_OF_DATE","Date (yyyy-mm-dd)", filter=True))
        schema.add_column(GridColumnFactory.create("ORIGINAL_NOTIONAL","Original Notional", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("FUND_CURRENCY","Currency", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("CURRENT_NOTIONAL","Current Notional", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("VAL","Market Value", filter=True,editable=True,valueFormatter= millions_format))
        schema.add_column(GridColumnFactory.create("PRICE","Price", filter=True,editable=True,valueFormatter= double_format))
        schema.add_column(GridColumnFactory.create("PRODUCT","Product", filter=True,editable=True ))
        schema.add_column(GridColumnFactory.create("CLASS","SubClass", filter=True,editable=True ))  
    return schema


def get_col_defs(gridId:str,dfData):
    schema = create_schema(gridId)
    colDefs = schema.get_columns_array()
    return colDefs

def get_formatted_data(gridId : str, dfData) :  
    schema = create_schema(gridId)
    arrayObj =schema.get_columns_arrayObj()
    formatted_df= pd.DataFrame(columns=dfData.columns)
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


def create_pivot_grid(gridid,dfData,colName,rowName,valName):
    pivotgrid = dash_pivottable.PivotTable(
            id="%s" % datetime.now(),
            data= dfData.to_dict("records"),
            cols=colName,
            rows=rowName,
            vals=valName,
            aggregatorName="Sum",
          )

    return pivotgrid
