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
        diff =[]
        for i in range(len(barcodeItemToFind['date_removed'])):
            date_in = barcodeItemToFind['date_added'][i]
            date_out = barcodeItemToFind['date_removed'][i]
            delta = date_out - date_in
            diff.append(str(delta).split('.', 2)[0])
        return jsonify({
        'brand_name':barcodeItemToFind['brand_name'],
        'item_name':barcodeItemToFind['item_name'],
        'size':barcodeItemToFind['size'],
        'servings_per_container':barcodeItemToFind['servings_per_container'],
        'units':barcodeItemToFind['units'],
        'barcode':barcodeItemToFind['barcode'],
        'quantity':barcodeItemToFind['quantity'],
        'date_added':barcodeItemToFind['date_added'],
        'date_removed':barcodeItemToFind['date_removed'],
        'difference': diff
        })

    tableFromID = mongo.db.psupplyID
    idItemToFind = tableFromID.find_one({'_id':ObjectId(foodID)})
    if (idItemToFind):
        diff =[]
        for i in range(len(idItemToFind['date_removed'])):
            date_in = idItemToFind['date_added'][i]
            date_out = idItemToFind['date_removed'][i]
            delta = date_out - date_in
            diff.append(str(delta).split('.', 2)[0])
        return jsonify({
        'brand_name':idItemToFind['brand_name'],
        'item_name':idItemToFind['item_name'],
        'quantity':idItemToFind['quantity'],
        'date_added':idItemToFind['date_added'],
        'date_removed':idItemToFind['date_removed'],
        'difference': diff
        })

    return "hi over there, can't find anything " + foodID

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if (request.method == 'POST'):
        barcode = request.form['barcode']
        itemBC = mongo.db.psupplyBC
        itemToIncrease = itemBC.find_one({'barcode':barcode})
        if (itemToIncrease):
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

            return "item added " + brandName + " " + itemName

    return "this route is only a POST"


@app.route('/insertman', methods=['GET', 'POST'])
def insertman():
    if (request.method=='POST'):
        date = []
        itemID = mongo.db.psupplyID

        brand_name = request.form['brand_name']
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        for i in range(quantity):
            date.append(datetime.datetime.now())
        itemID.insert({'brand_name':brand_name, 'item_name':item_name, 'quantity':quantity, 'date_added':date, 'date_removed':[]})

        return "Item added " + brand_name + " " + item_name

    return "This route is POST only"


@app.route('/adjustup/<foodID>')
def adjustup(foodID):

    barcode = mongo.db.psupplyBC
    barcodeItemToFind = barcode.find_one({'_id':ObjectId(foodID)})
    if (barcodeItemToFind):
        barcodeItemToFind['quantity'] += 1
        barcodeItemToFind['date_added'].append(datetime.datetime.now())
        barcode.save(barcodeItemToFind)
        return "found it in barcode table and added quantity 1 and added purchase date"

    tableFromID = mongo.db.psupplyID
    idItemToFind = tableFromID.find_one({'_id':ObjectId(foodID)})
    if (idItemToFind):
        idItemToFind['quantity'] += 1
        idItemToFind['date_added'].append(datetime.datetime.now())
        tableFromID.save(idItemToFind)
        return "found it in ID table and added quantity 1 and added purchase date"

    return "Didn't find any"

@app.route('/bcadjustup/<itemid>')
def bcgoup(itemid):
    barcode = mongo.db.psupplyBC
    barcodeItemToFind = barcode.find_one({'barcode':itemid})
    if (barcodeItemToFind):
        barcodeItemToFind['quantity'] += 1
        barcodeItemToFind['date_added'].append(datetime.datetime.now())
        barcode.save(barcodeItemToFind)
        return "found it in barcode table and added quantity 1 and added purchase date"
    return "Didn't find any"


@app.route('/adjustdown/<foodID>')
def adjustdown(foodID):

    barcode = mongo.db.psupplyBC
    barcodeItemToFind = barcode.find_one({'_id':ObjectId(foodID)})
    if (barcodeItemToFind):
        if (barcodeItemToFind['quantity'] > 1):
            barcodeItemToFind['quantity'] -= 1
            barcodeItemToFind['date_removed'].append(datetime.datetime.now())
            barcode.save(barcodeItemToFind)
            return "item decreased by one"
        if (barcodeItemToFind['quantity'] == 1):
            barcodeItemToFind['quantity'] = 0
            barcodeItemToFind['date_removed'].append(datetime.datetime.now())
            barcode.save(barcodeItemToFind)
            return "item is now at zero"
        else:
            return "Item is already at zero"

    tableFromID = mongo.db.psupplyID
    idItemToFind = tableFromID.find_one({'_id':ObjectId(foodID)})
    if (idItemToFind):
        if (idItemToFind['quantity'] > 1):
            idItemToFind['quantity'] -= 1
            idItemToFind['date_removed'].append(datetime.datetime.now())
            tableFromID.save(idItemToFind)
            return "item decresed by one"
        if (idItemToFind['quantity'] == 1):
            idItemToFind['quantity'] = 0
            idItemToFind['date_removed'].append(datetime.datetime.now())
            tableFromID.save(idItemToFind)
            return "item is now at zero"
        else:
            return "Item is already at zero"

    return "Sorry no item found"

@app.route('/bcadjustdown/<itembc>')
def bcgodown(itembc):
    barcode = mongo.db.psupplyBC
    barcodeItemToFind = barcode.find_one({'barcode':itembc})
    if (barcodeItemToFind):
        if (barcodeItemToFind['quantity'] > 1):
            barcodeItemToFind['quantity'] -= 1
            barcodeItemToFind['date_removed'].append(datetime.datetime.now())
            barcode.save(barcodeItemToFind)
            return "item decreased by one"
        if (barcodeItemToFind['quantity'] == 1):
            barcodeItemToFind['quantity'] = 0
            barcodeItemToFind['date_removed'].append(datetime.datetime.now())
            barcode.save(barcodeItemToFind)
            return "item is now at zero"
        else:
            return "Item is already at zero"

    return "Sorry no item found"


@app.route('/delete', methods=['GET', 'DELETE'])
def remove():
    if (request.method=='DELETE'):

        itemIdToDelete = request.form['item_id']

        barcode = mongo.db.psupplyBC
        barcodeItemToFind = barcode.find_one({'_id':ObjectId(itemIdToDelete)})
        if (barcodeItemToFind):
            barcode.remove(barcodeItemToFind)
            return "Removed item from the BARCODE table"

        tableFromID = mongo.db.psupplyID
        idItemToFind = tableFromID.find_one({'_id':ObjectId(itemIdToDelete)})
        if (idItemToFind):
            tableFromID.remove(idItemToFind)
            return "Removed item from the ID table"

    return "this is from API but did nOT go into DELETE"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=port)
