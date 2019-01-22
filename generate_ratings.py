from lib import nn_predict
from lib import company_data
import pandas as pd
import requests

def filterDF():
    df = pd.read_csv('lib/LSE.csv')
    rows_list = []
    for i, row in df.iterrows():
        symbol = row['Ticker']
        yahoo_fin_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=financialData".format(symbol)
        fin_dict = requests.get(yahoo_fin_url).json()
        if fin_dict['quoteSummary']['error'] is None:
            yahoo_balance_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=balanceSheetHistoryQuarterly".format(symbol)
            b_history = requests.get(yahoo_balance_url).json()['quoteSummary']['result'][0]['balanceSheetHistoryQuarterly']['balanceSheetStatements']
            if len(b_history) > 0 and 'totalCurrentLiabilities' in b_history[0]:
                dict1 = {'Ticker': row['Ticker'], 'Company': row['Company']}
                # get input row in dictionary format
                # key = col_name
                rows_list.append(dict1)
    out_df = pd.DataFrame(rows_list)  
    out_df.to_csv('LSE_Filtered.csv')

def getIndustries(source_df):
    ticker = ""
    rows_list = []
    for i, row in source_df.iterrows():
        ticker = row['Ticker']
        dict1 = {'Ticker': ticker, 'Name': row['Name'], 'Rating': row['Rating'], 'Industry': row['Industry']}
        try: 
            industry = nn_predict.getIndustryFor(ticker)
            if industry is not None and len(industry) > 0 and str(industry) is not "nan":
                dict1 = {'Ticker': ticker, 'Name': row['Name'], 'Rating': row['Rating'], 'Industry': industry}
        except : 
            pass
        rows_list.append(dict1)

    out_df = pd.DataFrame(rows_list, columns=['Ticker', 'Name', 'Rating', 'Industry'])  
    out_df.to_csv('tickers_industries_updated.csv')

def generate_ratings(source_df):
    """
    bad_co_list = [ 
        "ACEL"]
    for co in bad_co_list:
        this_symbol = co
        this_rating = int(getRatingFor(co))
    """
    rows_list = []
    for i, row in source_df.iterrows():
        current_progress = 5620
        if i < current_progress:
            continue
        ticker = row['Ticker']
        industry = ''
        dict1 = {'Ticker': ticker, 'Name': row['Name'], 'Rating': '-1', 'Industry': industry}
        try: 
            industry = nn_predict.getIndustryFor(ticker)
            if industry is not None and len(industry) > 0 and str(industry) is not "nan":
                dict1 = {'Ticker': ticker, 'Name': row['Name'], 'Rating': row['Rating'], 'Industry': industry}
            else:
                industry = ''

            rating = int(nn_predict.pullDataFor(ticker))
            dict1 = {'Ticker': ticker, 'Name': row['Name'], 'Rating': rating, 'Industry': industry}
        except : 
            pass
        rows_list.append(dict1)

    out_df = pd.DataFrame(rows_list, columns=['Ticker', 'Name', 'Rating', 'Industry'])  
    out_df.to_csv('A_Ratings_20190121.csv')

if __name__ == '__main__':
    generate_ratings(company_data.getData('lib/ticker_cache.csv'))
    #filterDF()