from appdb import getFundOverview_void,getDerivativesMetrics,getPositions,get_last_day_of_previous_month
import pandas as pd
from datetime import date

class Security:
    def __init__(self,name,cusip,isin,product,value,risk_level='medium'):
        self.name = name
        self.cusip= cusip
        self.isin = isin
        self.product = product
        self.value =value
        self.risk_level=risk_level.lower()  

    def update_value(self,new_value):
        self.value = new_value

    def __repr__(self):
        return f"{self.name} ({self.product}), Risk : {self.risk_level}) : ${self.value:,.2f}"


class FundPortfolio:
    def __init__(self,fund_name):
        self.fund_name=fund_name
        self.securities =[]

    def add_security(self,security):
        self.securities.append(security)

    def remove_asset(self,name):
        self.securities = [a for a in self.securities if a.name != name]

    def get_total_value(self):
        return sum(security.value for security in self.securities)

    def categorize_securities(self):
        categories ={}
        for security in self.securities:
            categories.setdefault(security.product,[]).append(security)
        return categories

    def filter_securities(self, product=None, min_value=None, max_value=None):
        result = self.securities
        if product :
            result= [a for a in result if a.product == product]
        if min_value is not None:
            result= [a for a in result if a.value>=min_value]
        if max_value is not None:
            result = [a for a in result if a.value<=max_value]
        return result

    def show_portfolio(self, filter_by=None, category_view=False):
        print(f"\nPortfolio for {self.fund_name}")

        if filter_by:
            filtered = self.filter_securities(**filter_by)
            for security in filtered:
                print(f" - {security}")
            total = sum(a.value for a in filtered)
            print(f"Filtered Total Value : $ {total:,.2f}")
        elif category_view:
            categorized = self.categorize_securities()
            for category,securities in categorized.items():
                print(f"\nCategory : {category.title()}")
                for security in securities:
                    print(f" - {security}")
                cat_total = sum(a.value for a in assets)
                print(f" Total in {category.title()} : ${cat.total:,.2f}")
            print(f"\n Overall Total Value : ${self.get_total_value():,.2f}")
        else:
            for security in self.securities:
                print(f" - {security}")
            print(f"Total Portfolio Value : ${self.get_total_value():,.2f}")

    def analyze_risk(self):
        risk_buckets = {"low":0, "medium":0,"high":0}
        for security in self.securities:
            if security.risk_level in risk_buckets:
                risk_buckets[security.risk_level]+= security.value
        
        total=self.get_total_value
        print("\n Risk Analysis")

        for level in ['low','medium','high']:
            percent = (risk_buckets[level] / total *100) if total else 0
            print(f" - {level.title()} Risk : ${risk_buckets[level]:,.2f} ({percent:.1f}%)")
        print(f"Total Portfolio Value: ${total:,.2f}")

if __name__ == "__main__":
    date_value=get_last_day_of_previous_month(date.today())
    dfPositions = getPositions(date_value)
 
    d= {}
    d = dfPositions.drop_duplicates(["AGGREGATE_NAME"])
 
    for index1,row1 in d.iterrows():
        filtered_df = dfPositions[dfPositions["AGGREGATE_NAME"]==row1["AGGREGATE_NAME"]]
        portfolio= FundPortfolio(row1["AGGREGATE_NAME"])
        for index,row in filtered_df.iterrows():
            portfolio.add_security(Security(row['DESCRIPTION'],row['CUSIP'],row['ISIN'],row['LEVEL1'],row['VAL']))

        portfolio.show_portfolio(filter_by={"product": "HY"})
 
