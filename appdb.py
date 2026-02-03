import pandas as pd
import os 
from datetime import   date 
from urllib import parse
from sqlalchemy import create_engine,text,bindparam
from sqlalchemy.engine import Engine
from dateutil.relativedelta import relativedelta
from sqlalchemy.dialects import registry

_ENGINE: Engine | None = None
#####Connectivity to Snowflake. Works only in Development Environment. Deployment doesn't work ######
# appdb.py
def get_engine() -> Engine:
    """
    Singleton Snowflake SQLAlchemy engine with connection pooling.
    """
    global _ENGINE
    if _ENGINE is None:
        registry.register('snowflake', 'snowflake.sqlalchemy', 'dialect')
        _ENGINE = create_engine(
            "snowflake://{user}:{password}@{account}/{database}/{schema}?role={role}&warehouse={warehouse}".format(
                user=os.environ["SNOWFLAKE_USER"],
                password=os.environ["SNOWFLAKE_PASSWORD"],
                account=os.environ["SNOWFLAKE_ACCOUNT"],
                database=os.environ["SNOWFLAKE_DATABASE"],
                schema=os.environ["SNOWFLAKE_SCHEMA"],
                role=os.environ["SNOWFLAKE_ROLE"],
                warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
                ocsp_fail_open=True  # important for Azure
            ),
            pool_size=5,          # max open connections
            max_overflow=2,       # temporary burst
            pool_timeout=30,      # seconds
            pool_recycle=1800,    # recycle every 30 min
            pool_pre_ping=True,   # detect dead connections
        )

    return _ENGINE

def get_last_day_of_previous_month(ASOF:date):
    return  ASOF + relativedelta(months=-3, day=31)
    
def getFundOverview() -> pd.DataFrame:
    engine=get_engine()
    sql = text("""select FUND_NAME,GAV_IN_FUND_CCY,TOTAL_LEVERAGE,REPO_LOAN_AMOUNT_FUND_CCY,MARGIN_POSTED_FUND_CCY,NET_CASH_AT_CUSTODY_FUND_CCY,CASH_RESERVES_FUND_CCY,CASH_NET_OF_RESERVES_FUND_CCY,CASH_NET_OF_RESERVES_AS_PCT_OF_GAV from ZAIS_PROD_MRT.FINCITE.FUND_OVERVIEW_REPORT""")        
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)

        # with get_connection() as ctx:
        #     with ctx.cursor() as cs:
        #         cs.execute("select FUND_NAME,GAV_IN_FUND_CCY,TOTAL_LEVERAGE,REPO_LOAN_AMOUNT_FUND_CCY,MARGIN_POSTED_FUND_CCY,NET_CASH_AT_CUSTODY_FUND_CCY,CASH_RESERVES_FUND_CCY,CASH_NET_OF_RESERVES_FUND_CCY,CASH_NET_OF_RESERVES_AS_PCT_OF_GAV from ZAIS_PROD_MRT.FINCITE.FUND_OVERVIEW_REPORT" )
        #         return pd.DataFrame(
        #              cs.fetchall(),
        #              columns=[c[0] for c in cs.description]
        #         )

def getDerivativesMetrics(date_value) -> pd.DataFrame:
    engine = get_engine()
    sql = text("""select * from ZAIS_PROD_MRT.FINCITE.DERIVATIVES_METRICS where ASOF=:date_value""").bindparams(bindparam("date_value",date_value))
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)
                                    
    
    # with get_connection() as ctx:
    #     with ctx.cursor() as cs:
    #         cs.execute("select * from ZAIS_PROD_MRT.FINCITE.DERIVATIVES_METRICS where ASOF=%s", (date_value,))
    #         return pd.DataFrame(
    #                 cs.fetchall(),
    #                 columns=[c[0] for c in cs.description]
    #         )
 
def getPositions(date_value) -> pd.DataFrame:
    engine = get_engine()
    sql = text("""select * ,AGGREGATE_NAME AS FUND_NAME from ZAIS_PROD_MRT.FINCITE.VW_CRYSTAL_POSITIONS where as_of_date=:date_value""").bindparams(bindparam("date_value",date_value))
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)
    # with get_connection() as ctx:
    #     with ctx.cursor() as cs:
    #         cs.execute("select * ,AGGREGATE_NAME AS Fund_Name from ZAIS_PROD_MRT.FINCITE.VW_CRYSTAL_POSITIONS where as_of_date=%s", (date_value,))
    #         return pd.DataFrame(
    #                 cs.fetchall(),
    #                 columns=[c[0] for c in cs.description]
    #         )

def getFx(date_value):
    engine = get_engine()
    sql = text("""select fx.Currency_Index,fx.Mid_Price,fx.As_Of_Date from  fx_History_eod as fx where  Currency_index in ('EUR') and fx.As_Of_Date in (%s)""",(date_value,))
    with engine.connect() as conn:
        return pd.read_sql(sql,conn)
    # with get_connection() as ctx:
    #     with ctx.cursor() as cs:
    #         cs.execute("select fx.Currency_Index,fx.Mid_Price,fx.As_Of_Date from  fx_History_eod as fx where  Currency_index in ('EUR') and fx.As_Of_Date in (%s)",(date_value,))
    #         return pd.DataFrame(
    #                 cs.fetchall()                    
    #         )