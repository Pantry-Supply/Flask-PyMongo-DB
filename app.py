from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_pymongo import ObjectId
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
    output=[]

    itemBC = mongo.db.psupplyBC
    for bc in itemBC.find():
        output.append({
        'brand_name':bc['brand_name'],
        'item_name':bc['item_name'],
        'quantity':bc['quantity'],
        'item_id':str(bc['_id'])
        })

    itemID = mongo.db.psupplyID
    for item in itemID.find():
        output.append({
        'brand_name':item['brand_name'],
        'item_name':item['item_name'],
        'quantity':item['quantity'],
        'item_id':str(item['_id'])
        })

    return jsonify({'result': output})

@app.route('/getone/<foodID>')
def getone(foodID):

    barcode = mongo.db.psupplyBC
    barcodeItemToFind = barcode.find_one({'_id':ObjectId(foodID)})
    if (barcodeItemToFind):
        return jsonify({
        'brand_name':barcodeItemToFind['brand_name'],
        'item_name':barcodeItemToFind['item_name'],
        'size':barcodeItemToFind['size'],
        'servings_per_container':barcodeItemToFind['servings_per_container'],
        'units':barcodeItemToFind['units'],
        'barcode':barcodeItemToFind['barcode'],
        'quantity':barcodeItemToFind['quantity'],
        'date_added':barcodeItemToFind['date_added'],
        'date_removed':barcodeItemToFind['date_removed']
        })

    tableFromID = mongo.db.psupplyID
    idItemToFind = tableFromID.find_one({'_id':ObjectId(foodID)})
    if (idItemToFind):
        return jsonify({
        'brand_name':idItemToFind['brand_name'],
        'item_name':idItemToFind['item_name'],
        'quantity':idItemToFind['quantity'],
        'date_added':idItemToFind['date_added'],
        'date_removed':idItemToFind['date_removed']
        })

    return "hi over there, can't find anything " + foodID

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if (request.method == 'POST'):
        barcode = request.form['barcode']
        itemBC = mongo.db.psupplyBC
        itemToIncrease = itemBC.find_one({'barcode':barcode})
        if (itemToIncrease):
            print("there is something in already")
            itemToIncrease['quantity'] +=1
            itemToIncrease['date_added'].append(datetime.datetime.now())
            itemBC.save(itemToIncrease)
            output = {'brand_name': itemToIncrease['brand_name'], 'item_name': itemToIncrease['item_name'], 'quantity':itemToIncrease['quantity']}
            return jsonify({'result': output})
        else:
            print("this is a new item")
            date=[]
            source = requests.get('https://api.nutritionix.com/v1_1/item?upc=%s&appId=84f8ed7f&appKey=d476c24cdcdf18749e8ca0e5b9bce022' % barcode)
            brandName = source.json()["brand_name"]
            itemName = source.json()["item_name"]
            serveSize = source.json()["nf_serving_size_qty"]
            servePerCont = source.json()["nf_servings_per_container"]
            units = source.json()["nf_serving_size_unit"]
            date.append(datetime.datetime.now())

            itemBC.insert({'brand_name':brandName, 'item_name':itemName, 'size':serveSize, 'servings_per_container':servePerCont, 'units':units, 'barcode':barcode, 'quantity':1, 'date_added':date, 'date_removed':[]})

            return "item added" + brandName + " " + itemName

    return "this route is only a POST"


@app.route('/insertman', methods=['GET', 'POST'])
def insertman():
    if (request.method=='POST'):
        date = []
        itemID = mongo.db.psupplyID

        brand_name = request.form['brand_name']
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        for i in range(int(quantity)):
            date.append(datetime.datetime.now())

        itemID.insert({'brand_name':brand_name, 'item_name':item_name, 'quantity':quantity, 'date_added':date, 'date_removed':[]})

        return "Item added " + brand_name + " " + item_name

    return "This route is POST only"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=port)
