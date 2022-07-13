from bson import ObjectId
from flask import Flask, render_template, jsonify, request, url_for, redirect

import jwt
import datetime
import hashlib
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

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
    bid = book.select_one('div.detail > div.title > a')['href'].split('barcode=')[1]

    doc = {
        'title' : title, 'img' : img, 'rank' : rank,'done':done,
    }
    db.books.insert_one(doc)
# all_users = list(db.users.find({},{'_id':False}))


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

# 북 디테일(상세페이지)
@app.route('/bookDetail')
def book_detail():
    token_receive = request.cookies.get('mytoken')

    try:
        # 로그인 정보
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})

        # 책 크롤링
        bid = request.args.get("bid")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(f'http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&barcode={bid}',
                            headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')

        book_name = ''
        try:
            book_name = soup.select_one(
                '#container > div:nth-child(4) > form > div.box_detail_point > h1 > strong').text.strip()
        except AttributeError as e:
            if book_name == None:
                book_name = ''

        book_img_url = ''
        try:
            book_img_url = soup.select_one(
                '#container > div:nth-child(4) > form > div.box_detail_info > div.box_detail_cover > div > a > img')[
                "src"]
        except AttributeError as e:
            if book_img_url == None:
                book_img_url = ''

        author = ''
        try:
            author = soup.select_one(
                '#container > div:nth-child(4) > form > div.box_detail_point > div.author > span:nth-child(1) > a').text.strip()
        except AttributeError as e:
            if author == None:
                author = ''
        print('author : ' + author)

        publisher = ''
        try:
            publisher = soup.select_one(
                '#container > div:nth-child(4) > form > div.box_detail_point > div.author > span:nth-child(3) > a').text.strip()
        except AttributeError as e:
            if publisher == None:
                publisher = ''
        print('publisher : ' + publisher)

        desc = ''
        try:
            desc = soup.select_one(
                '#container > div:nth-child(7) > div.content_left > div:nth-child(5) > div:nth-child(10)').text.strip()
        except AttributeError as e:
            if desc == None:
                desc = ''
        print('desc : ' + desc)

        # 책 정보(book_chart)
        book_chart = {
            'book_name': book_name,
            'book_img_url': book_img_url,
            'author': author,
            'publisher': publisher,
            'desc' : desc,
        }
        print(book_chart)

        # 댓글 정보(comments)
        comments = list(db.comments.find({'bid': bid}))

        for comment in comments:
            comment['comment_id'] = str(comment["_id"])

        # 도서 정보(books)
        books = db.books.find_one({'bid': bid})
        books["bookId"] = str(books["_id"])
        # print(books)

        return render_template("detailpage.html", bid=bid, user_info=user_info, book_chart=book_chart, books=books,
                               comments=comments)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 코멘트 생성
@app.route('/createComment', methods=['POST'])
def create_comment():
    user_id_receive = request.form['user_id_give']
    nickname_receive = request.form['nickname_give']
    bid_receive = request.form['bid_give']
    comment_receive = request.form['comment_give']

    doc = {
        'userId': user_id_receive,
        'nickname': nickname_receive,
        'bid': bid_receive,
        'comment': comment_receive
    }
    db.comments.insert_one(doc)

    return jsonify({'msg': '댓글이 등록되었습니다!'})


# 도서 댓글 삭제(delete)
@app.route('/delComment', methods=['POST'])
def delete_comment():
    user_id_receive = request.form['user_id_give']
    comment_id_receive = request.form['comment_id_give']

    # commentObject key값 받기

    doc = {
        '_id': ObjectId(comment_id_receive),
        'userId': user_id_receive
    }

    db.comments.delete_one(doc)

    return jsonify({'msg': '댓글이 삭제되었습니다!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)