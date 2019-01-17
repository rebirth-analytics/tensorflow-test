from __future__ import print_function
import tensorflow as tf
import numpy as np
import lib.test_inputs as test_inputs

"""Load model from export_dir, predict on input data, expected output is 5."""
export_dir = './tmp/'
checkpoint_path = tf.train.latest_checkpoint(export_dir)
saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
rating_cache = {}

def load_graph():
    ret_list = []
    with tf.Session() as sess:
        saver.restore(sess, checkpoint_path)
        output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": test_inputs.in_data})
        for i in output:
            ret_list.append(np.asscalar(i))
    return ret_list

def rate(arr):
    try:
        rating = -1
        export_dir = './tmp/'
        checkpoint_path = tf.train.latest_checkpoint(export_dir)
        saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
        with tf.Session() as sess:
            saver.restore(sess, checkpoint_path)
            output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": [arr]})
            rating = np.asscalar(output[0])
        return str(rating)
    except Exception as e:
        print(str(e))

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

def pullDataFor(symbol):
    """
        run quarterly over a set of tickers to update current ratings for public companies
    """
    if symbol in rating_cache:
        return rating_cache[symbol]

    import requests
    data_dict = {}
    scaling_factor = 1000
    yahoo_fin_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=financialData".format(symbol)
    fin_dict = requests.get(yahoo_fin_url).json()
    if fin_dict['quoteSummary']['error'] is not None:
        return -1

    fin_stats_dict = fin_dict['quoteSummary']['result'][0]['financialData']
    yahoo_balance_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=balanceSheetHistoryQuarterly".format(symbol)
    b_history = requests.get(yahoo_balance_url).json()['quoteSummary']['result'][0]['balanceSheetHistoryQuarterly']['balanceSheetStatements']
    if len(b_history) < 1 or 'totalCurrentLiabilities' not in b_history[0]:
        return -1

    b_dict = b_history[0]
    yahoo_income_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=incomeStatementHistoryQuarterly".format(symbol)
    income_dict = requests.get(yahoo_income_url).json()['quoteSummary']['result'][0]['incomeStatementHistoryQuarterly']['incomeStatementHistory'][0]
    yahoo_cash_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=cashflowStatementHistoryQuarterly".format(symbol)
    cash_dict = requests.get(yahoo_cash_url).json()['quoteSummary']['result'][0]['cashflowStatementHistoryQuarterly']['cashflowStatements'][0]
    x_int = lambda d, k: 0 if k not in d or d[k] is None else int(d[k]) / scaling_factor
    data_dict['totalDebt'] = int(fin_stats_dict['totalDebt']['raw'] / scaling_factor)
    data_dict['totalLiabilities'] = int(b_dict['totalLiab']['raw']) / scaling_factor
    data_dict['currentLiabilities'] = x_int(b_dict['totalCurrentLiabilities'],'raw')
    data_dict['currentAssets'] = int(b_dict['totalCurrentAssets']['raw']) / scaling_factor
    data_dict['totalAssets'] = x_int(b_dict['totalAssets'], 'raw') 
    data_dict['shareholderEquity'] = x_int(b_dict['totalStockholderEquity'], 'raw') 
    if('longTermDebt' not in b_dict):
        data_dict['longTermDebt'] = data_dict['totalDebt']
    else:
        data_dict['longTermDebt'] = x_int(b_dict['longTermDebt'], 'raw') 
    data_dict['interestExpense'] = x_int(income_dict['interestExpense'],'raw')
    data_dict['netIncome'] = int(income_dict['netIncome']['raw'] / scaling_factor)
    data_dict['operatingExpense'] = int(income_dict['totalOperatingExpenses']['raw'] / scaling_factor)
    data_dict['sales'] = int(income_dict['totalRevenue']['raw'] / scaling_factor)
    data_dict['earningPreInterestTax'] = int(income_dict['incomeBeforeTax']['raw'] / scaling_factor) + data_dict['interestExpense']

    data_dict['fixedAssets'] = 0
    if('propertyPlantEquipment' in b_dict):
        data_dict['fixedAssets'] = x_int(b_dict['propertyPlantEquipment'], 'raw')

    data_dict['depreciation'] = 104000
    if('depreciation' in b_dict):
        data_dict['depreciation'] = x_int(cash_dict['depreciation'], 'raw')

    data_dict['capEx'] = 132000
    if('capitalExpenditures' in cash_dict):
        data_dict['capEx'] = x_int(cash_dict['capitalExpenditures'], 'raw') 

    data_dict['inventoryChange'] = 0
    if 'inventory' in b_dict and 'raw' in b_dict['inventory']:
        prev_b_dict = b_history[1]
        if 'inventory' in prev_b_dict and 'raw' in prev_b_dict['inventory']:
            data_dict['inventoryChange'] = x_int(b_dict['inventory'], 'raw') - x_int(prev_b_dict['inventory'], 'raw')
    
    if 'raw' not in fin_stats_dict['currentRatio']:
        data_dict['currentRatio'] = float(data_dict['currentAssets'] / data_dict['currentLiabilities'])
    else:
        data_dict['currentRatio'] = float(fin_stats_dict['currentRatio']['raw'])

    if 'raw' not in fin_stats_dict['returnOnEquity']:
        data_dict['equityReturn'] = float(data_dict['netIncome'] / data_dict['shareholderEquity'])
    else:
        data_dict['equityReturn'] = float(fin_stats_dict['returnOnEquity']['raw'])

    rating_cache[symbol] = rateFromDict(data_dict)
    return rating_cache[symbol]

def rateFromDict(dict):
    int_expense = dict['interestExpense']
    if int_expense < 100:
        int_expense = 100
        
    equityAssetRatio = 1
    if RepresentsInt(dict['fixedAssets']) and int(dict['fixedAssets']) != 0:
        equityAssetRatio = (dict['shareholderEquity'] + dict['longTermDebt'] ) / dict['fixedAssets']
        
    expenseSalesRatio = 0.25
    if RepresentsInt(dict['operatingExpense']) and int(dict['operatingExpense']) != 0 and int(dict['sales']) != 0:
        expenseSalesRatio = dict['operatingExpense'] / dict['sales']

    totalRatio = dict['totalAssets'] / dict['totalLiabilities']
    if 'currentRatio' not in dict:
        dict['currentRatio'] = dict['currentAssets'] / dict['currentLiabilities']
    timesInterestEarned = dict['earningPreInterestTax'] / int_expense
    incomeCapexRatio = (dict['netIncome'] + dict['depreciation']) / (dict['capEx'] + dict['inventoryChange'])
    debtIncomeRatio = dict['totalDebt'] / dict['netIncome']
    arr = [totalRatio, dict['currentRatio'], equityAssetRatio, dict['equityReturn'],
        timesInterestEarned, incomeCapexRatio, debtIncomeRatio, expenseSalesRatio]
    return rate(arr)

if __name__ == '__main__':
    #for input in test_inputs.in_data:
        #print("""Company: {0}, Rating: {1}""".format(input['company_name'], rateFromDict(input)))
    print("not supported")
