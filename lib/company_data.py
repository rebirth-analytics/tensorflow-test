import pandas as pd
import math

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

def getIndustryAveragesDF(df):
    return df.groupby(['Industry'])['Rating'].agg(lambda x: x.unique().mean())

def getAverageFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        industry = df.iloc[0].Industry
        return averages_df[averages_df.Industry == industry].iloc[0].CurrentRating
    return "Industry Not Found"

def getAverageForIndustry(industry):
    return averages_df[averages_df.Industry == industry].iloc[0].CurrentRating

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

def getAddressFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        return df.iloc[0].Address
    return "No Address Found"

def getResiliencyFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        return round(df.iloc[0].Resiliency, 2)
    return 0

def getDefaultProbFor(symbol):
    df = cache_df[cache_df.Ticker == symbol]
    if not df.empty:
        oscore = df.iloc[0].DefaultProb
        if oscore != 0 and oscore != -1:
            ep = math.exp(oscore)
            return round(float(ep / (1 + ep)), 3) * 100
    return -1

if __name__ == '__main__':
    print("not supported")