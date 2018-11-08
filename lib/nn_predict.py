from __future__ import print_function
import tensorflow as tf
import numpy as np
import lib.test_inputs as test_inputs

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

def rateFromDict(dict):
    int_expense = dict['interestExpense']
    if int_expense < 100:
        int_expense = 100
        
    totalRatio = dict['totalAssets'] / dict['totalLiabilities']
    currentRatio = dict['currentAssets'] / dict['currentLiabilities']
    equityAssetRatio = (dict['shareholderEquity'] + dict['longTermDebt'] ) / dict['fixedAssets']
    timesInterestEarned = dict['earningPreInterestTax'] / int_expense
    incomeCapexRatio = (dict['netIncome'] + dict['depreciation']) / (dict['capEx'] + dict['inventoryChange'])
    debtIncomeRatio = dict['totalDebt'] / dict['netIncome']
    expenseSalesRatio = dict['operatingExpense'] / dict['sales']
    arr = [totalRatio, currentRatio, equityAssetRatio, dict['equityReturn'],
        timesInterestEarned, incomeCapexRatio, debtIncomeRatio, expenseSalesRatio]
    return rate(arr)

if __name__ == '__main__':
    for input in test_inputs.in_data:
        print("""Company: {0}, Rating: {1}""".format(input['company_name'], rateFromDict(input)))