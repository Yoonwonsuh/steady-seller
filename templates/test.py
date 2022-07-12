import requests
from bs4 import BeautifulSoup

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?orderClick=d79',headers=headers)


soup = BeautifulSoup(data.text, 'html.parser')




books = soup.select('#main_contents > ul > li')
for book in books[:20]:
 bid = book.select_one('div.detail > div.title > a')['href'].split('barcode=')[1]
 print(bid)