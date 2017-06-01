from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from pprint import pprint
import jsonify
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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=port)
