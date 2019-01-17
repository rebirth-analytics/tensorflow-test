from lib import nn_predict
from lib import company_data
import pandas as pd

def generate_ratings():
    companies_df = company_data.getSECData()
    this_symbol = ""
    """
    bad_co_list = [ 
        "ACEL"]
    for co in bad_co_list:
        this_symbol = co
        this_rating = int(getRatingFor(co))
    """
    for i, row in companies_df.iterrows():
        current_progress = 3389
        if i < current_progress:
            continue
        this_symbol = row['Ticker']
        #print("symbol is {}".format(this_symbol))
        if row['Rating'] == -1:
            try: 
                rating = int(nn_predict.pullDataFor(this_symbol))
                companies_df.at[i,'Rating'] = rating
            except : 
                pass
        if  i >= current_progress:
            print("writing to row {}".format(str(i)))
            companies_df.to_csv('public_ratings.csv')

if __name__ == '__main__':
    generate_ratings()