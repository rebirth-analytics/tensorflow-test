"""
This script runs the FlaskWebProject application using a development server.
"""

from os import environ
from flask import Flask, jsonify, request, render_template
from lib import nn_predict
 
app = Flask(__name__)

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

@app.template_filter('rate')
def rate(args):
    if(len(args) == 21):
        return nn_predict.rate(args)
    else:
        return "-1"

@app.route('/')
@app.route('/home')
def home():
    return render_template('form.html')

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
