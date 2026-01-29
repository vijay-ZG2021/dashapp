import snowflake.connector
import pandas as pd
from  dash import Dash,html,dcc
from dotenv import load_dotenv
import os 
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

# appdb.py
import snowflake.connector
import os

def get_connection():
    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        ocsp_fail_open=True  # important for Azure
    )


#####Connectivity to Snowflake. Works only in Development Environment. Deployment doesn't work ######

def get_last_day_of_previous_month(ASOF:date):
    today = ASOF 
    last_day_prev_month = today + relativedelta(months=-2, day=31)
    #last_day_of_previous_month = first_day_of_last_month - timedelta(days=1)
    return last_day_prev_month

load_dotenv()

app = Dash(__name__)
server = app.server

#ctx= snowflake.connector.connect(
 #   user=os.environ.get('user'),
  #  password = os.environ.get('password'),
   # account = os.environ.get('account'),
    #Warehouse= os.environ.get('Warehouse'),
    #database=os.environ.get('database'),
    #schema = os.environ.get('schema')
#)

def getFundOverview():
    try:
        ctx = get_connection()
        cs = ctx.cursor()
        cs.execute("select FUND_NAME,GAV_IN_FUND_CCY,TOTAL_LEVERAGE,REPO_LOAN_AMOUNT_FUND_CCY,MARGIN_POSTED_FUND_CCY,NET_CASH_AT_CUSTODY_FUND_CCY,CASH_RESERVES_FUND_CCY,CASH_NET_OF_RESERVES_FUND_CCY,CASH_NET_OF_RESERVES_AS_PCT_OF_GAV from ZAIS_PROD_MRT.FINCITE.FUND_OVERVIEW_REPORT" )
        data = cs.fetchall()
        hdrs = pd.DataFrame(cs.description)
        df = pd.DataFrame(data)
        df.columns= hdrs['name']
        return df
    finally:
        cs.close()
    ctx.close()

def getDerivativesMetrics(date_value):
    try:
        ctx = get_connection()
        cs = ctx.cursor()
        cs.execute("select * from ZAIS_PROD_MRT.FINCITE.DERIVATIVES_METRICS where ASOF=%s", (date_value,))
        data = cs.fetchall()
        hdrs =pd.DataFrame(cs.description)
        df = pd.DataFrame(data)
        df.columns = hdrs['name']
        return df
    finally:
        cs.close()
    ctx.close()

def getPositions(date_value):
    try:
        ctx = get_connection()
        cs = ctx.cursor()
        cs.execute("select * ,AGGREGATE_NAME AS Fund_Name from ZAIS_PROD_MRT.FINCITE.VW_CRYSTAL_POSITIONS where as_of_date=%s", (date_value,))
        data = cs.fetchall()
        hdrs =pd.DataFrame(cs.description)
        df = pd.DataFrame(data)
        df.columns = hdrs['name']
        return df
    finally:
        cs.close()
    ctx.close()


def getFx(date_value):
    try:
        prev_date_value= get_last_day_of_previous_month(date_value)
        ctx = get_connection()
        cs = ctx.cursor()
        cs.execute("select fx.Currency_Index,fx.Mid_Price,fx.As_Of_Date from  fx_History_eod as fx where  Currency_index in ('EUR') and fx.As_Of_Date in (%s)",(date_value,))
        data = cs.fetchall()
        df = pd.DataFrame(data)
        return df
    finally:
        cs.close()
    ctx.close()

