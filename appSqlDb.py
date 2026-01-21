import pymssql
from dotenv import load_dotenv
import os 
from flask import Flask
from  dash import Dash,html,dcc
from datetime import datetime, date, timedelta
import pandas as pd

load_dotenv() 
#####Connectivity to Sql Server using PYMSSQL######

conn = pymssql.connect(
            server=os.environ.get('sqlserver'),
            user=os.environ.get('sqluser'),
            password=os.environ.get('sqlpassword'),
            database=os.environ.get('sqldb'),
            as_dict=True
        )  

def get_last_day_of_previous_month(ASOF:date):
    today = ASOF
    first_day_of_current_month = date(today.year,today.month, 1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_previous_month

def get_previous_date(date_value:date):
    today = date_value
    first = date(today.year,today.month, 1)
    last_month = first -  timedelta(days=1)
    return last_month

def getPositions(date_value):
    try:
        cursor = conn.cursor()
        start_date = get_previous_date(date_value) 
        end_date = datetime(date_value.year,date_value.month,date_value.day)
        query = """
        select Description,asOfDate,originalNotional,currentNotional,
        marketValue,Price,security_name,fund_name as Fund_Name,CUSIP,ISIN,Product,SubClass from [reports].[vw_ActiveFundPositions_monthEndV1]
        where fund_id=%s and asofdate BETWEEN %s AND %s 
        and type in  ('Bond','Cash','Commitment','Drawdown','Equity')
        """
        cursor.execute(query,(2,start_date,end_date))
        #cursor.execute("select top 10 * from history.MonthEndIntegratedPositionsReport where fundid=%s and asofdate>%s",(2,'2025/3/31'))       #cursor.execute(SQL_QUERY)
        data = cursor.fetchall()
        hdrs =pd.DataFrame(cursor.description)
        df = pd.DataFrame(data)
        df.columns = hdrs[0]
        return df
    except ValueError:
       print(ValueError)
    finally:
        cursor.close()
    conn.close()
    
def getDerivativesMetrics(date_value):
    try:
        cursor = conn.cursor()
        start_date = get_previous_date(date_value) + timedelta(days=1)
        end_date = datetime(date_value.year,date_value.month,date_value.day)
        query = """
        select Description,asOfDate,originalNotional,currentNotional,
        marketValue,Price,security_name,fund_name as Fund_Name from [reports].[vw_ActiveFundPositions_monthEndV1]
        where fund_id=%s and asofdate BETWEEN %s AND %s
        and type not in ('Bond','Cash','Commitment','Drawdown','Generic')
        """
        cursor.execute(query,(2,start_date,end_date))
        data = cursor.fetchall()
        hdrs =pd.DataFrame(cursor.description)
        df = pd.DataFrame(data)
        df.columns = hdrs[0]
        return df
    except ValueError:
       print(ValueError)
    finally:
        cursor.close()
    conn.close()

def getFundOverview(date_value):
    try:
        cursor = conn.cursor()
        start_date = get_previous_date(date_value)  
        end_date = datetime(date_value.year,date_value.month,date_value.day)
        query = """
        exec ZaisMark.[monthend].[SaveMonthEndFundNAV] @FundId = %s, @Asofdate=%s, @Prevdate=%s
        """
        cursor.execute(query,(2, end_date,start_date))

        result_sets=[]

        while True:
            rows = cursor.fetchall()
            result_sets.append(rows)

            if not cursor.nextset():
                break

        for ids,result in enumerate(result_sets):
            #print(f"result set {ids+1}:")
            df = pd.DataFrame(result)

        df.insert(0,'Fund_Name','CDO Opportunity')
        df.insert(1,'AsOfDate', date_value)
        return df
    except ValueError:
       print(ValueError)
    finally:
        cursor.close()
    conn.close()


date_value=get_last_day_of_previous_month(date.today())
getFundOverview(date_value)
