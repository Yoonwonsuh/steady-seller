from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.ziyis.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

client = MongoClient('mongodb+srv://test:sparta@cluster0.kx1zt.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('login.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("index", msg="메인 페이지 입니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/index')
def page():
    token_receive = request.cookies.get('mytoken')

    try:
        # 로그인 정보
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"userId": payload["id"]})

        return render_template("index.html", user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    doc = {
        "userId": id_receive,  # 아이디
        "password": pw_hash,  # 비밀번호
        "nickname": nickname  # 닉네임
    }

    db.user.insert_one(doc)

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        user_info = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'user_info': user_info})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?orderClick=d79', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

books = soup.select('#main_contents > ul > li')
for book in books:
    title = book.select_one('div.detail > div.title > a > strong').text
    img = book.select_one('div.cover > a > img')['src']
    rank = book.select_one('div.cover > a > strong').text
    done = 0
    bid = book.select_one('div.detail > div.title > a')['href'].split('barcode=')[1]

    doc = {
        'title': title, 'img': img, 'rank': rank, 'done': done, 'bid': bid
    }
    db.books.insert_one(doc)


# all_users = list(db.users.find({},{'_id':False}))

# main_contents > ul > li:nth-child(6) > div.detail > div.subtitle


@app.route("/books", methods=["POST"])
def book_post():
    url_receive = request.form['url_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    return jsonify({'msg': '저장 완료!'})


@app.route("/books", methods=["GET"])
def movie_get():
    book_list = list(db.books.find({}, {'_id': False}))
    return jsonify({'books': book_list})


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
            'desc': desc,
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
    app.run('0.0.0.0', port=8000, debug=True)
