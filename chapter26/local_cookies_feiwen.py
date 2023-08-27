import requests
import logging
import asyncio
import re
import time
import pymongo
from pyquery import PyQuery as pq

MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_NAME = 'story827'
MONGO_DB_NAME = MONGO_NAME
MONGO_COLLECTION_NAME = MONGO_NAME

client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_CONNECTION_STRING]

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

stories_url = 'https://www.xn--pxtr7m.com/threads/216723/profile'
username = '3072912320@qq.com'
password = '128314'
cookies_file = 'cookies_feiwen.txt'

headers = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

def use_saved_cookies(session):
    session.headers = headers
    jar = requests.cookies.RequestsCookieJar()
    
    with open(cookies_file, 'r') as f:
        cookies = eval(f.read())
    for cookie in cookies:
        jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
    session.cookies.update(jar)

    # response = session.get(stories_url)

    # print(session.cookies)
    # print(session.cookies.get_dict())

def scrape_api(session, url):
    logging.info('scraping %s', url)
    try:
        response = session.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)

def scrape_index(session, index):
    return scrape_api(session, stories_url)

def parse_index(html):
    doc = pq(html)
    article = doc('.article-title .font-1').text()
    chapters = doc('.panel-body .btn').items()
    for chapter in chapters:
        chapters_url = chapter.attr('href')
        yield chapters_url

def scrape_detail(session, detail_url):
    return scrape_api(session, detail_url)

def parse_detail(html):
    doc = pq(html)
    chapter_name = doc('.text-center .h3').text()
    chapter_brief = doc('.text-center .h5').text()
    contents = doc('.main-text.no-selection span').items()
    content_list = []
    for content in contents:
        content_list.append(content.text())
    chapter_content = content_list[0]
    return {
        'chapter_name': chapter_name,
        'chapter_brief': chapter_brief,
        'chapter_content': chapter_content,
    }

def save_data(data):
    logging.debug('saving data %s', data)
    collection.update_one({
        'name': data.get('chapter_name')
    }, {
        '$set': data
    }, upsert=True)

def main():
    session = requests.session()
    use_saved_cookies(session)
    index_html = scrape_index(session, 1)
    urls = parse_index(index_html)
    for url in urls:
        detail_html = scrape_detail(session, url)
        data = parse_detail(detail_html)
        save_data(data)

if __name__ == '__main__':
    main()