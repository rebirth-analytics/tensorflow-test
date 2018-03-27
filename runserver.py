"""
This script runs the FlaskWebProject application using a development server.
"""

from os import environ
from flask import Flask, jsonify
from lib import nn_predict
 
app = Flask(__name__)

def get_json_response(rows):
    response = jsonify(result = rows)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/get_rating')
def rating():
    return get_json_response(nn_predict.load_graph())

@app.route('/')
@app.route('/home')
def home():
    return "Hello World!"

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
