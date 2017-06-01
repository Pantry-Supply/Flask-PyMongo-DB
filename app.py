from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from pprint import pprint
import json
import requests
import os
import datetime
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('dbAddress')
app.config['MONGO_URI'] = os.environ.get('dbURI')

port = int(os.environ.get('PORT', 5000))

mongo = PyMongo(app)

@app.route('/getall')
def getall():
    return "hello world"

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':

        temp = request.form['temperature']
        # temp1 = request.data['barcode']
        # temp = json.loads(request.data['barcode'])
        # print(temp)
        print(request.form['temperature'])
        return temp


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=port)
