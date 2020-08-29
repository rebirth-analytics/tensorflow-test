from os import environ, remove
from flask import Flask, jsonify, request, render_template, make_response, abort, send_file
from io import BytesIO
from xlrd import open_workbook, XLRDError
from lib import nn_predict, company_data, db_utils, edd_parser
import time
import datetime
import math
import zipfile
import pdfkit
import http
import pdftotext
 
app = Flask(__name__)
session = {}

def test_book(filename):
    try:
        open_workbook(filename)
    except XLRDError:
        return False
    else:
        return True

def get_report_period(year):
    currentMonth = datetime.datetime.now().month
    currentYear = datetime.datetime.now().year
    if currentMonth < 2:
        return "Y {0}".format(str(currentYear - 2))
    return "Y {0}".format(str(currentYear - 1))
        
def get_json_response(rows):
    response = jsonify(result = rows)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/get_test_result')
def test_result():
    return get_json_response(nn_predict.load_graph())

@app.route('/locate')
def locate():
    uuid = request.args.get('record', default='', type = str)
    if(db_utils.is_uuid(uuid)):
        data = db_utils.locate_report_data(uuid)
        return render_template('rating_report.html', data=data)
    return abort(404)

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
    year = request.args.get('year', default='2018', type = str)
    rating = 0
    company = "No Financial Data Available"
    average = 0
    industry = "Unknown"
    address = ""
    report_period = get_report_period(year)
    resiliency = .5
    bankruptcy_prob = -1
    rating_change = 0
    try: 
        rating = int(company_data.getRatingFor(symbol))
        previous_rating = int(company_data.getPreviousRatingFor(symbol))
        rating_change = str(rating - previous_rating)
        if int(rating_change) > 0:
            rating_change = "+{}".format(rating_change)
        company = "Company Name Not Found"
        company = company_data.getCompanyName(symbol)
        industry = company_data.getIndustryFor(symbol)
        address = company_data.getAddressFor(symbol)
        resiliency = company_data.getResiliencyFor(symbol)
        bankruptcy_prob = company_data.getDefaultProbFor(symbol)
    except : 
        print("Error calling company_data.getRatingFor()")
        pass
    try: 
        if industry is not None and str(industry) != 'nan' and industry != "Unknown":
            average = company_data.getAverageFor(symbol)
        else:
            industry = "(Unlisted)"
    except : 
        print("Error calling company_data.getAverageFor()")
        pass
    data = {'current_rating': int(rating), 
        'rating_change': rating_change,
        'symbol': symbol, 
        'date_generated': datetime.datetime.today(),
        'report_period': report_period,
        'address': address,
        'resiliency_ratio': resiliency,
        'default_probability': bankruptcy_prob,
        'company_name': company,
        'industry': industry, 
        'industry_rating': average}
    return render_template('symbol_result.html', data=data)

def get_dict_from_args(rargs):
    rdict = {}
    rdict['address'] = rargs.get('address', default='(Not Given)', type = str)
    rdict['company'] = rargs.get('company', default='(Not Given)', type = str)
    rdict['industry'] = rargs.get('industry', default='(Not Given)', type = str)
    rdict['period'] = rargs.get('period', default='(Not Given)', type = str)
    rdict['totalAssets'] = rargs.get('totalAssets', default=0, type = float)
    rdict['totalLiabilities'] = rargs.get('totalLiabilities', default=0, type = float)
    rdict['currentAssets'] = rargs.get('currentAssets', default=0, type = float)
    rdict['prevCurrentAssets'] = rargs.get('prevCurrentAssets', default=0, type = float)
    rdict['currentLiabilities'] = rargs.get('currentLiabilities', default=0, type = float)
    rdict['prevCurrentLiabilities'] = rargs.get('prevCurrentLiabilities', default=0, type = float)
    rdict['shareholderEquity'] = rargs.get('shareholderEquity', default=0, type = float)
    rdict['longTermDebt'] = rargs.get('longTermDebt', default=0, type = float)
    rdict['fixedAssets'] = rargs.get('fixedAssets', default=0, type = float)
    rdict['depreciation'] = rargs.get('depreciation', default=0, type = float)
    rdict['interestExpense'] = rargs.get('interestExpense', default=0, type = float)
    rdict['equityReturn'] = rargs.get('equityReturn', default=0, type = float)
    rdict['operatingIncome'] = rargs.get('operatingIncome', default=0, type = float)
    rdict['capEx'] = rargs.get('capEx', default=0, type = float)
    rdict['inventoryChange'] = rargs.get('inventoryChange', default=0, type = float)
    rdict['totalDebt'] = rargs.get('totalDebt', default=0, type = float)
    rdict['netIncome'] = rargs.get('netIncome', default=0, type = float)
    rdict['prevNetIncome'] = rargs.get('prevNetIncome', default=0, type = float)
    rdict['operatingExpense'] = rargs.get('operatingExpense', default=0, type = float)
    rdict['sales'] = rargs.get('sales', default=0, type = float)
    rdict['workingCapital'] = rargs.get('workingCapital', default=-1, type = float)
    rdict['totalCashFromOperatingActivities'] = rargs.get('totalCashFromOperatingActivities', default=0, type = float)
    return rdict

def get_data_from_args(args):
    rdict = get_dict_from_args(args)
    return get_data_from_dict(rdict)

def get_data_from_dict(rdict):
    rating = nn_predict.rateFromDict(rdict)
    average = -1
    if rdict['industry'] is not None and str(rdict['industry']) != 'nan' and rdict['industry'] != "Unknown":
        average = company_data.getAverageForIndustry(rdict['industry'])
    oscore = nn_predict.getBankruptFromDict(rdict)
    ep = -0.99
    bankruptcy_prob = round(float(ep / (1 + ep)), 3) * 100
    if oscore != 0 and oscore != -1:
        try:
            ep = math.exp(oscore)
        except OverflowError:
            print("getDefaultProbFor symbol: {}, score: {}".format(rdict['company'], oscore))
            pass
    bankruptcy_prob = round(float(ep / (1 + ep)), 3) * 100
    resiliency = nn_predict.getResiliencyFromDict(rdict)
    data = {'current_rating': int(rating), 
        'rating_change': 0,
        'is_public': 0,
        'date_generated': datetime.datetime.today(),
        'report_period': rdict['period'],
        'address': rdict['address'],
        'resiliency_ratio': resiliency,
        'default_probability': bankruptcy_prob,
        'company_name': rdict['company'],
        'industry': rdict['industry'], 
        'industry_rating': average}
    return data

@app.route('/rating_result')
def rating_result():
    data = get_data_from_args(request.args)
    return render_template('result.html', data=data)
    
@app.route('/rating_pdf')
def rating_pdf():
    data = get_data_from_args(request.args)
    rendered_template = render_template('pdf_result.html', data=data) 

    pdf = pdfkit.from_string(rendered_template, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'rebirth_report'
    return response

def rating_result_OLD():
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
        print("Found {} rows in spreadsheet".format(str(max_row)))
        row_count = max_row - 1
        rating = 0
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            #Create pdf for each row
            for row in range(1, max_row):
                if s.cell(row,0).value == '':
                    break
                row_dict = {}
                for name, col in zip(col_names, range(s.ncols)):
                    value  = (s.cell(row,col).value)
                    if name.value in ['period','address', 'company', 'industry']:
                        row_dict[name.value] = str(value)
                    else:
                        try : value = float(value)
                        except : pass
                        row_dict[name.value] = value

                pdf = None
                data = get_data_from_dict(row_dict)
                rendered_template = render_template('pdf_result.html', data=data) 
                pdf = pdfkit.from_string(rendered_template, False)

                zdata = zipfile.ZipInfo('{0}_{1}_rating_report.pdf'.format(row_dict['company'].replace(",","").replace(".",""), row_dict['period'][-4:]))
                zdata.date_time = time.localtime(time.time())[:6]
                zdata.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(zdata, pdf)
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='reports.zip', as_attachment=True)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/home')
@app.route('/excel')
@app.route('/batch_rating')
def batch_rating():
    return render_template('batch_rating.html')


@app.route('/edd_helper')
def edd_helper():
    #return render_template('edd_helper.html')
    return "Not Available"

@app.route('/generate_edd', methods=['POST'])
def generate_edd():
    #for key in ['pdf_filename', 'excel_filename']:
    report_data = process_file(request, 'pdf_filename') 
    if report_data == {}:
        abort(500)
    filename = edd_parser.create_document(report_data)
    return send_file(filename, attachment_filename=filename, as_attachment=True)

def process_file(request, key):
    report_data = {}
    if key not in request.files:
        print('ERROR')
    else:
        f = request.files[key]
        if f.filename == '':
            print('ERROR')
        else:
            if f:
                report_filename = f.filename
                f.save(report_filename)
                if key == 'pdf_filename':
                    with open(report_filename, "rb") as in_file:
                        pdf = pdftotext.PDF(in_file)
                        is_personal_pdf = False
                        for line in pdf[0].split("\n"):
                            words = line.split()
                            if len(words) > 2 and words[0] == "Date" and words[2] == "Birth:":
                               is_personal_pdf = True 
                               break
                        if is_personal_pdf:
                            report_data = edd_parser.parse_person_pdf(pdf)
                        else:
                            report_data = edd_parser.parse_company_pdf(pdf)
                else: #excel report
                    report_data = {'Report': 'Excel'}
                
                remove(report_filename)
                        
                # validate file now
    return report_data

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
