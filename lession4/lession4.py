from lxml import html
from pprint import pprint
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

client = MongoClient('localhost', 27017)
db = client['news-lentaru']
last24 = db.last24
topnews = db.topnews

main_url = 'https://lenta.ru'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

response = requests.get(main_url, headers=header)
dom = html.fromstring(response.text)

last24_news = dom.xpath("//a[contains(@class,'_compact')]")

for news in last24_news:
    news_data = {}
    title = news.xpath(".//span/text()")[0]
    link = main_url + news.xpath(".//span/../../@href")[0]
    date = f"{link.split('/')[4]}.{link.split('/')[5]}.{link.split('/')[6]}"
    ids = link.split('/')[7]

    news_data['_id'] = ids
    news_data['title'] = title
    news_data['source'] = main_url
    news_data['date'] = date
    news_data['link'] = link

    try:
        last24.insert_one(news_data)
    except dke:
        pass

for news in last24.find({}):
    pprint(news)

topnews_news = dom.xpath("//a[contains(@class, '_topnews')]")

for news in topnews_news:
    topnews_data = {}

    if len(news.xpath(".//span/text()")) != 0:
        top_title = news.xpath(".//span/text()")[0]
        top_link = main_url + news.xpath(".//span/../../@href")[0]
        top_date = f"{top_link.split('/')[4]}.{top_link.split('/')[5]}.{top_link.split('/')[6]}"
        top_ids = top_link.split('/')[7]
    else:
        top_title = news.xpath(".//h3/text()")[0]
        top_link = main_url + news.xpath(".//h3/../../@href")[0]
        top_date = f"{top_link.split('/')[4]}.{top_link.split('/')[5]}.{top_link.split('/')[6]}"
        top_ids = top_link.split('/')[7]


    topnews_data['_id'] = top_ids
    topnews_data['title'] = top_title
    topnews_data['source'] = main_url
    topnews_data['date'] = top_date
    topnews_data['link'] = top_link

    try:
        topnews.insert_one(topnews_data)
    except dke:
        pass



# for news in topnews.find({}):
#
#     pprint(news)
