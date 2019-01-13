from __future__ import print_function
import tensorflow as tf
import numpy as np
#import lib.test_inputs as test_inputs
import pandas as pd

companies_df = pd.read_csv('lib/secwiki_tickers.csv')
"""Load model from export_dir, predict on input data, expected output is 5."""
export_dir = './tmp/'
checkpoint_path = tf.train.latest_checkpoint(export_dir)
saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)

def load_graph():
    ret_list = []
    with tf.Session() as sess:
        saver.restore(sess, checkpoint_path)
        output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": test_inputs.in_data})
        for i in output:
            ret_list.append(np.asscalar(i))
    return ret_list

def rate(arr):
    rating = -1
    export_dir = './tmp/'
    checkpoint_path = tf.train.latest_checkpoint(export_dir)
    saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
    with tf.Session() as sess:
        saver.restore(sess, checkpoint_path)
        output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": [arr]})
        rating = np.asscalar(output[0])
    return str(rating)

def ratingNumToGrade(rating):
    if(rating == 10):
        return "AAA" 
    elif(rating  == 9):
        return "AA"
    elif(rating  == 8):
        return "A"
    elif(rating  == 7):
        return "BBB"
    elif(rating  == 6):
        return "BB"
    elif(rating  == 5):
        return "B"
    elif(rating  == 4):
        return "CCC"
    elif(rating  == 3):
        return "CC"
    elif(rating  == 2):
        return "C"
    elif(rating  == 1):
        return "D"
    elif(rating  == 0):
        return "SUB D"

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def getRatingFor(symbol):
    from yahoofinancials import YahooFinancials
    yahoo_financials = YahooFinancials(symbol)
    import requests
    data_dict = {}
    scaling_factor = 1000
    yahoo_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=financialData".format(symbol)
    fin_stats_dict = requests.get(yahoo_url).json()
    x_int = lambda s: 0 if s is None else int(s) / scaling_factor
    data_dict['totalDebt'] = int(fin_stats_dict['quoteSummary']['result'][0]['financialData']['totalDebt']['raw'] / scaling_factor)
    bal_history = yahoo_financials.get_financial_stmts('quarterly', 'balance')['balanceSheetHistoryQuarterly'][symbol]
    balance_dict = list(bal_history[0].values())[0]
    cash_dict = list(yahoo_financials.get_financial_stmts('quarterly', 'cash')['cashflowStatementHistoryQuarterly'][symbol][0].values())[0]
    data_dict['inventoryChange'] = 0
    if 'inventory' in balance_dict:
        prev_balance_dict = list(bal_history[1].values())[0]
        if 'inventory' in prev_balance_dict:
            data_dict['inventoryChange'] = x_int(balance_dict['inventory']) - x_int(prev_balance_dict['inventory'])
    
    data_dict['interestExpense'] = x_int(yahoo_financials.get_interest_expense()) 
    data_dict['netIncome'] = x_int(yahoo_financials.get_net_income()) 
    data_dict['totalLiabilities'] = x_int(balance_dict['totalLiab']) 
    data_dict['currentLiabilities'] = x_int(balance_dict['totalLiab']) 
    data_dict['currentAssets'] = x_int(balance_dict['totalCurrentAssets']) 
    data_dict['totalAssets'] = x_int(balance_dict['totalAssets']) 
    data_dict['fixedAssets'] = x_int(balance_dict['propertyPlantEquipment']) 
    data_dict['shareholderEquity'] = x_int(balance_dict['totalStockholderEquity']) 
    data_dict['longTermDebt'] = x_int(balance_dict['longTermDebt']) 
    data_dict['operatingExpense'] = x_int(yahoo_financials.get_total_operating_expense()) 
    data_dict['sales'] = x_int(yahoo_financials.get_total_revenue()) 
    data_dict['earningPreInterestTax'] = x_int(yahoo_financials.get_income_before_tax()) + data_dict['interestExpense']
    data_dict['netIncome'] = x_int(yahoo_financials.get_net_income()) 
    data_dict['depreciation'] = x_int(cash_dict['depreciation']) 
    data_dict['capEx'] = x_int(cash_dict['capitalExpenditures']) 
    data_dict['equityReturn'] = float(data_dict['netIncome'] / data_dict['shareholderEquity'])

    return rateFromDict(data_dict)

def rateFromDict(dict):
    int_expense = dict['interestExpense']
    if int_expense < 100:
        int_expense = 100
        
    equityAssetRatio = 1
    if RepresentsInt(dict['fixedAssets']) and int(dict['fixedAssets']) != 0:
        equityAssetRatio = (dict['shareholderEquity'] + dict['longTermDebt'] ) / dict['fixedAssets']
        
    expenseSalesRatio = 0.25
    if RepresentsInt(dict['operatingExpense']) and int(dict['operatingExpense']) != 0:
        expenseSalesRatio = dict['operatingExpense'] / dict['sales']

    totalRatio = dict['totalAssets'] / dict['totalLiabilities']
    currentRatio = dict['currentAssets'] / dict['currentLiabilities']
    timesInterestEarned = dict['earningPreInterestTax'] / int_expense
    incomeCapexRatio = (dict['netIncome'] + dict['depreciation']) / (dict['capEx'] + dict['inventoryChange'])
    debtIncomeRatio = dict['totalDebt'] / dict['netIncome']
    expenseSalesRatio = dict['operatingExpense'] / dict['sales']
    arr = [totalRatio, currentRatio, equityAssetRatio, dict['equityReturn'],
        timesInterestEarned, incomeCapexRatio, debtIncomeRatio, expenseSalesRatio]
    return rate(arr)

def getCompanyName(symbol):
    test = companies_df[companies_df.Ticker==symbol]
    if not (test.empty):
        return list(test.Name.values)[0]
    return ""

if __name__ == '__main__':
    #for input in test_inputs.in_data:
        #print("""Company: {0}, Rating: {1}""".format(input['company_name'], rateFromDict(input)))
    print(getRatingFor('NFLX'))