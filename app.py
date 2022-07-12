from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.kx1zt.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?orderClick=d79',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')


books = soup.select('#main_contents > ul > li')
for book in books[:20]:
    title = book.select_one('div.detail > div.title > a > strong').text
    img = book.select_one('div.cover > a > img')['src']
    rank = book.select_one('div.cover > a > strong').text
    done = 0

    doc = {
        'title' : title, 'img' : img, 'rank' : rank,'done':done,
    }
    db.books.insert_one(doc)


#main_contents > ul > li:nth-child(6) > div.detail > div.subtitle
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/books", methods=["POST"])
def book_post():
    url_receive = request.form['url_give']


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    return jsonify({'msg':'저장 완료!'})

@app.route("/books", methods=["GET"])
def movie_get():
    book_list = list(db.books.find({}, {'_id': False}))
    return jsonify({'books':book_list})

@app.route("/books/done", methods=["POST"])
def rank_done():
    rank_receive = request.form['rank_give']
    db.books.update_one({'rank': rank_receive}, {'$set': {'done': 1}})
    return jsonify({'msg': '등록 완료!'})

@app.route("/books/cancel", methods=["POST"])
def cancel_done():
    rank_receive = request.form['rank_give']
    db.books.update_one({'rank': rank_receive}, {'$set': {'done': 0}})
    return jsonify({'msg': '취소 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)