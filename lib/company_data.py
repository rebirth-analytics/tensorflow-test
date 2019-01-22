import pandas as pd

averages_df = pd.read_csv('lib/industry_averages.csv')
sec_df = pd.read_csv('lib/secwiki_tickers.csv')
cache_df = pd.read_csv('lib/ticker_cache.csv')

def getSECData():
    return sec_df

def getData(file):
    return pd.read_csv(file)

def getCompanyName(symbol):
    test = cache_df[cache_df.Ticker==symbol]
    if not (test.empty):
        return list(test.Name.values)[0]
    return ""

def getAverageFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        industry = df.iloc[0].Industry
        return averages_df[averages_df.Industry == industry].iloc[0].Rating
    return "Industry Not Found"

def getIndustryFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        return df.iloc[0].Industry
    return "Ticker Not Found"

def getRatingFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        return df.iloc[0].Rating
    return -1

if __name__ == '__main__':
    print("not supported")