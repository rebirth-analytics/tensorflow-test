from __future__ import print_function
import tensorflow as tf
import numpy as np
import requests
import math

"""Load model from export_dir, predict on input data, expected output is 5."""
export_dir = './tmp/'
checkpoint_path = tf.train.latest_checkpoint(export_dir)
saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
rating_cache = {}
base_query_url = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
scaling_factor = 1000

"""
def load_graph():
    import lib.test_inputs as test_inputs
    ret_list = []
    with tf.Session() as sess:
        saver.restore(sess, checkpoint_path)
        output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": test_inputs.in_data})
        for i in output:
            ret_list.append(np.asscalar(i))
    return ret_list
"""

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

def rate_arrays(arr_list):
    rating_list = []
    try:
        rating = -1
        export_dir = './tmp/'
        checkpoint_path = tf.train.latest_checkpoint(export_dir)
        saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)
        with tf.Session() as sess:
            saver.restore(sess, checkpoint_path)
            for arr in arr_list:
                output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": [arr]})
                rating = np.asscalar(output[0])
                rating_list.add(str(rating))
        return rating_list
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


def getModuleUrlFor(symbol, module):
    return "{0}{1}?modules={2}".format(base_query_url, symbol, module)
    
def getAddressFor(symbol):
    yahoo_url = getModuleUrlFor(symbol, "assetProfile")
    profile_dict = requests.get(yahoo_url).json()
    if profile_dict['quoteSummary']['error'] is not None or len(profile_dict['quoteSummary']['result']) < 1:
        return None

    d = profile_dict['quoteSummary']['result'][0]['assetProfile']
    address = ""
    if 'address1' in d:
        address = d['address1']
        if 'address2' in d:
            address += " {0}".format(d['address2'])
    loc = ""
    if 'city' in d:
        loc = d['city']
        if 'zip' in d:
            loc = "{0} {1}".format(d['city'], d['zip'])
            if 'state' in d:
                loc = "{0} {1} {2}".format(d['city'], d['state'], d['zip'])
    elif 'state' in d:
        loc = d['state']
    elif 'zip' in d:
        loc = d['zip']

    return "{0} {1}".format(address, loc)

def getResiliencyFromDict(dict):
    return float(int(dict['totalDebt']) / int(dict['sales']))

def getResiliencyFor(symbol, index=0, total_debt = 0):
    """
        totalDebt / totalRevenue
    """

    yahoo_income_url = getModuleUrlFor(symbol, "incomeStatementHistory")
    income = requests.get(yahoo_income_url).json()['quoteSummary']['result'][0]['incomeStatementHistory']['incomeStatementHistory'][index]

    if 'totalRevenue' in income :
        r = income['totalRevenue']
        if 'raw' in r and int(r['raw']) != 0:
            if total_debt == 0:
                yahoo_fin_url = getModuleUrlFor(symbol, "financialData")
                f_dict = requests.get(yahoo_fin_url).json()
                if f_dict['quoteSummary']['error'] is not None:
                    return -1 
                fin_data = f_dict['quoteSummary']['result'][0]['financialData']
                if 'totalDebt' in fin_data:
                    total_debt  = int(fin_data['totalDebt']['raw'] / scaling_factor)
                else:
                    return -1 
            else:
                total_debt = total_debt / scaling_factor

            totalRevenue = int(r['raw'] / scaling_factor)
            return float(total_debt / totalRevenue)

    return -1

def getFinDict(symbol, index=0):
    import datetime
    fin_dict = {}
    currentYear = datetime.datetime.now().year
    prevYear = int(currentYear) - 2
    yahoo_balance_url = getModuleUrlFor(symbol, "balanceSheetHistory")
    b_history = requests.get(yahoo_balance_url).json()['quoteSummary']['result'][0]['balanceSheetHistory']['balanceSheetStatements']
    if len(b_history) < 3 or 'totalCurrentLiabilities' not in b_history[index] or 'totalCurrentAssets' not in b_history[index] or 'totalCurrentLiabilities' not in b_history[index + 1]:
        return None
    
    fin_dict['b0'] = b_history[index]
    fin_dict['b1'] = b_history[index + 1]
    #if int(b_history[0]['endDate']['fmt'].split("-")[0]) == prevYear:
    #    fin_dict['b1'] = b_history[index]

    yahoo_cash_url = getModuleUrlFor(symbol, "cashflowStatementHistory")
    cash_hist = requests.get(yahoo_cash_url).json()['quoteSummary']['result'][0]['cashflowStatementHistory']['cashflowStatements']
    if len(cash_hist) < 3 or 'netIncome' not in cash_hist[index] or 'totalCashFromOperatingActivities' not in cash_hist[index] or 'raw' not in cash_hist[index]['totalCashFromOperatingActivities']:
        return None
    fin_dict['c0'] = cash_hist[index]
    fin_dict['c1'] = cash_hist[index + 1]
    #if int(cash_hist[0]['endDate']['fmt'].split("-")[0]) == prevYear:
    #    fin_dict['c1'] = cash_hist[index]
    return fin_dict

def getBankruptFromDict(dic):
    if dic is not None:
        """
        x_int = lambda d, k: 0 if k not in d or d[k] is None else int(d[k]) / scaling_factor
        fields = ['totalLiabilities','currentLiabilities','prevCurrentLiabilities','currentAssets',
            'prevCurrentAssets','totalAssets','netIncome','prevNetIncome','totalCashFromOperatingActivities']
        for field in fields:
            dic[field] = x_int(dic, field)
        """
        if (dic['workingCapital'] == -1):
            dic['workingCapital'] = dic['currentAssets'] - dic['currentLiabilities']
        dic['changeInWorkingCapital'] = dic['workingCapital'] - (dic['prevCurrentAssets'] - dic['prevCurrentLiabilities'])
        dic['fundsFromOps'] = dic['totalCashFromOperatingActivities'] - dic['changeInWorkingCapital']
        return oscoreFromDict(dic)

def getBankruptFor(symbol, index=0, dic={}):
    """
        Calculate Ohlson O-score for a company
    """
    d = getFinDict(symbol, index)
    if d is not None:
        b_dict = d['b0']
        x_int = lambda d, k: 0 if k not in d or d[k] is None else int(d[k]) / scaling_factor
        if 'totalLiabilities' not in dic:
            dic['totalLiabilities'] = int(b_dict['totalLiab']['raw']) / scaling_factor
        else:
            dic['totalLiabilities'] = x_int(dic,'totalLiabilities')
        if 'currentLiabilities' not in dic:
            dic['currentLiabilities'] = int(b_dict['totalCurrentLiabilities']['raw']) / scaling_factor
        else:
            dic['currentLiabilities'] = x_int(dic,'currentLiabilities')
        dic['prevCurrentLiabilities'] = int(d['b1']['totalCurrentLiabilities']['raw']) / scaling_factor
        if 'currentAssets' not in dic:
            dic['currentAssets'] = int(b_dict['totalCurrentAssets']['raw']) / scaling_factor
        else:
            dic['currentAssets'] = x_int(dic,'currentAssets')
        dic['prevCurrentAssets'] = int(d['b1']['totalCurrentAssets']['raw']) / scaling_factor
        if 'totalAssets' not in dic:
            dic['totalAssets'] = int(b_dict['totalAssets']['raw']) / scaling_factor
        else:
            dic['totalAssets'] = x_int(dic,'totalAssets')
        dic['workingCapital'] = dic['currentAssets'] - dic['currentLiabilities']
        dic['changeInWorkingCapital'] = dic['workingCapital'] - (dic['prevCurrentAssets'] - dic['prevCurrentLiabilities'])
        if 'totalCashFromOperatingActivities' not in dic:
            dic['totalCashFromOperatingActivities'] = int(d['c0']['totalCashFromOperatingActivities']['raw']) / scaling_factor
        else:
            dic['totalCashFromOperatingActivities'] = x_int(dic,'totalCashFromOperatingActivities')
        dic['fundsFromOps'] = dic['totalCashFromOperatingActivities'] - dic['changeInWorkingCapital']
        if 'netIncome' not in dic:
            dic['netIncome'] = int(d['c0']['netIncome']['raw']) / scaling_factor
        else:
            dic['netIncome'] = x_int(dic,'netIncome')
        dic['prevNetIncome'] = int(d['c1']['netIncome']['raw']) / scaling_factor
        return oscoreFromDict(dic)

def oscoreFromDict(dict):
    gnp = 108
    X = 0
    if dict['totalLiabilities'] > dict['totalAssets']:
        X = 1
    Y = 0
    if (dict['netIncome'] + dict['prevNetIncome']) < 0:
        Y = 1
    o_score = -1.32 - (.407 * math.log(dict['totalAssets'] / gnp)) \
        + (6.03 * float(dict['totalLiabilities'] / dict['totalAssets'])) \
        - (1.43 * float(dict['workingCapital'] / dict['totalAssets'])) \
        - (.0757 * float(dict['currentLiabilities'] / dict['currentAssets'])) \
        - (1.72 * X) \
        - (2.37 * float(dict['fundsFromOps'] / dict['totalLiabilities'])) \
        + (.285 * Y) \
        - (.521 * float((dict['netIncome'] - dict['prevNetIncome']) / (math.fabs(dict['netIncome']) + math.fabs(dict['prevNetIncome']))))
    return o_score

def getIndustryFor(symbol):
    yahoo_url = getModuleUrlFor(symbol, "assetProfile")
    profile_dict = requests.get(yahoo_url).json()
    if profile_dict['quoteSummary']['error'] is not None or len(profile_dict['quoteSummary']['result']) < 1:
        return None

    return profile_dict['quoteSummary']['result'][0]['assetProfile']['industry']
    
def pullDataFor(symbol, index = 0, total_debt=0):
    """
        run quarterly over a set of tickers to update current ratings for public companies
    if symbol in rating_cache:
        return rating_cache[symbol]
    """

    data_dict = {}
    data_dict['totalDebt'] = int(total_debt) / scaling_factor
    if int(total_debt) == 0:
        yahoo_fin_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=financialData".format(symbol)
        fin_dict = requests.get(yahoo_fin_url).json()
        if fin_dict['quoteSummary']['error'] is not None:
            return -1
        fin_stats_dict = fin_dict['quoteSummary']['result'][0]['financialData']
        data_dict['totalDebt'] = int(fin_stats_dict['totalDebt']['raw'] / scaling_factor)

    yahoo_balance_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=balanceSheetHistory".format(symbol)
    b_history = requests.get(yahoo_balance_url).json()['quoteSummary']['result'][0]['balanceSheetHistory']['balanceSheetStatements']
    if len(b_history) < (index + 2) or 'totalCurrentLiabilities' not in b_history[index]:
        return -1

    b_dict = b_history[index]
    yahoo_income_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=incomeStatementHistory".format(symbol)
    income_dict = requests.get(yahoo_income_url).json()['quoteSummary']['result'][0]['incomeStatementHistory']['incomeStatementHistory'][index]
    yahoo_cash_url="https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?modules=cashflowStatementHistory".format(symbol)
    cash_dict = requests.get(yahoo_cash_url).json()['quoteSummary']['result'][0]['cashflowStatementHistory']['cashflowStatements'][index]
    x_int = lambda d, k: 0 if k not in d or d[k] is None else int(d[k]) / scaling_factor
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
    data_dict['operatingIncome'] = int(income_dict['operatingIncome']['raw'] / scaling_factor) + data_dict['interestExpense']

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
        prev_b_dict = b_history[index + 1]
        if 'inventory' in prev_b_dict and 'raw' in prev_b_dict['inventory']:
            data_dict['inventoryChange'] = x_int(b_dict['inventory'], 'raw') - x_int(prev_b_dict['inventory'], 'raw')
    
    data_dict['currentRatio'] = float(data_dict['currentAssets'] / data_dict['currentLiabilities'])

    data_dict['equityReturn'] = float(data_dict['netIncome'] / data_dict['shareholderEquity'])

    rating_cache[symbol] = rateFromDict(data_dict)
    return rating_cache[symbol]

def rateFromDict(dict):
    int_expense = int(dict['interestExpense'])
    if int_expense < 100:
        int_expense = 100
        
    equityAssetRatio = 1
    if RepresentsInt(dict['fixedAssets']) and int(dict['fixedAssets']) != 0:
        equityAssetRatio = (int(dict['shareholderEquity']) + int(dict['longTermDebt']) ) / int(dict['fixedAssets'])
        
    expenseSalesRatio = 0.25
    if RepresentsInt(dict['operatingExpense']) and int(dict['operatingExpense']) != 0 and int(dict['sales']) != 0:
        expenseSalesRatio = int(dict['operatingExpense']) / int(dict['sales'])

    totalRatio = int(dict['totalAssets']) / int(dict['totalLiabilities'])
    if 'currentRatio' not in dict:
        dict['currentRatio'] = int(dict['currentAssets']) / int(dict['currentLiabilities'])
    timesInterestEarned = int(dict['operatingIncome']) / int_expense
    if int(dict['capEx']) == 0 and int(dict['operatingExpense']) != 0:
        dict['capEx'] = dict['operatingExpense'] #capEx should never be zero
    if int(dict['netIncome']) == 0:
        dict['netIncome'] = -1
    incomeCapexRatio = (int(dict['netIncome']) + int(dict['depreciation'])) / (int(dict['capEx']) + int(dict['inventoryChange']))
    debtIncomeRatio = int(dict['totalDebt']) / int(dict['netIncome'])
    arr = [totalRatio, float(dict['currentRatio']), equityAssetRatio, float(dict['equityReturn']),
        timesInterestEarned, incomeCapexRatio, debtIncomeRatio, expenseSalesRatio]
    return rate(arr)

def get_altman_score(dict):
    """
        Get Altman Z-score from data dict
        z-score equals 1.2 A + 1.4 B + 3.3 C + 0.6 D + E
        where:
        A = (Current Assets - Current liabilities) / Total Assets
        B = Retained Earnings / Total Assets
        C = earnings pre interest and tax / Total Assets
        D = Market Value of Equity (Market Cap)/ Total Liabilities
        E = Sales / Total Assets 
    """
    return 4

if __name__ == '__main__':
    #for input in test_inputs.in_data:
        #print("""Company: {0}, Rating: {1}""".format(input['company_name'], rateFromDict(input)))
    print("not supported")
