from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

import certifi
ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.mt2g7.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('mypage.html')


@app.route("/books", methods=["GET"])
def rank_done():
    book_list = list(db.books.find({}, {'_id': False}))
    return jsonify({'books': book_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)