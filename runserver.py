"""
This script runs the FlaskWebProject application using a development server.
"""

from os import environ
from flask import Flask, jsonify, request, render_template
from xlrd import open_workbook, XLRDError
from lib import nn_predict
 
app = Flask(__name__)

def test_book(filename):
    try:
        open_workbook(filename)
    except XLRDError:
        return False
    else:
        return True
        
def get_json_response(rows):
    response = jsonify(result = rows)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/get_test_result')
def test_result():
    return get_json_response(nn_predict.load_graph())

@app.route('/get_rating')
def get_rating():
    args = request.args.getlist('arg', type = float)
    rate(args)

@app.route('/get_rating')
def rate(args):
    """
    if(len(args) == 21):
        return nn_predict.rate(args)
    else:
    """
    return "-1 NOT AVAILABLE"

@app.route('/rate_symbol')
def rate_symbol():
    """
        Rates latest data from yahoo finance for given stock symbol
    """
    data = {'rating': '0', 'test': ''}
    symbol = request.args.get('symbol', default='AAPL', type = str)
    rating = 0
    company = "No Financial Data Available"
    average = 0
    industry = "Unknown"
    try: 
        rating = int(nn_predict.getRatingFor(symbol))
        company = "Company Name Not Found"
        company = nn_predict.getCompanyName(symbol)
        industry = nn_predict.getIndustryFor(symbol)
        average = nn_predict.getAverageFor(symbol)
    except : 
        print("Error calling nn_predict.getRatingFor()")
        pass
    data = {'rating': str(rating), 'symbol': symbol, 'company': company, 'test': '', 'industry': industry, 'average': average}
    return render_template('symbol_result.html', data=data)

@app.route('/rating_result')
def rating_result():
    args = request.args.getlist('arg', type = float)
    compliance = request.args.get('compliance', default=0, type = int)
    office_ratio = request.args.get('officeRatio', default=0, type = float)
    windows_ratio = request.args.get('windowsRatio', default=0, type = float)
    sql_ratio = request.args.get('SQLRatio', default=0, type = float)
    win_factor = (1 - windows_ratio) * 10
    office_factor = (1 - office_ratio) * 10
    sql_factor = (1 - sql_ratio) * 10
    #for input in test_inputs.in_data:
        #print("""Company: {0}, Rating: {1}""".format(input['company_name'], nn_predict.rateFromDict(input)))
    #rating = 100 - int(compliance) - (5 * (3 - int(rate(args)))) - win_factor - office_factor - sql_factor
    #data = {'rating': str(rating), 'windows_ratio': windows_ratio, 'sql_ratio': sql_ratio, 'office_ratio': office_ratio}
    data = {'rating': str(90), 'windows_ratio': windows_ratio, 'sql_ratio': sql_ratio, 'office_ratio': office_ratio}
    return render_template('result.html', data=data)
    
@app.route('/rate_excel', methods = ['GET', 'POST'])
def rate_excel():
    data = {'rating': '0', 'test': ''}
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        wb = open_workbook(f.filename)
        test_string = ''
        s = wb.sheet_by_index(0)
        col_names = s.row(0)
        max_row = s.nrows
        row_count = max_row - 1
        rating = 0
        for row in range(1, max_row):
            row_dict = {}
            for name, col in zip(col_names, range(s.ncols)):
                value  = (s.cell(row,col).value)
                try : value = float(value)
                except : pass
                row_dict[name.value] = value
            try: rating += int(nn_predict.rateFromDict(row_dict))
            except : 
                print("Error calling nn_predict.rateFromDict()")
                pass
        data = {'rating': str(float(rating / row_count)), 'test': test_string}
        return render_template('excel_result.html', data=data)

def home():
    return render_template('form.html')

@app.route('/')
@app.route('/home')
@app.route('/excel')
@app.route('/batch_rating')
def batch_rating():
    return render_template('batch_rating.html')


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
