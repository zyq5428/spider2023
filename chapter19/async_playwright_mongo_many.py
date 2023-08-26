import logging
from os.path import exists
from os import makedirs
import json
import asyncio
import re
import time
from playwright.async_api import Playwright, async_playwright, expect, TimeoutError
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

INDEX_URL = 'https://spa2.scrape.center/page/{index}'
TIMEOUT = 30
TOTAL_PAGE = 10

'''
设置json文件保存路径
'''
RESULTS_DIR = 'results824'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)

'''
设置MONGO异步访问
'''
MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_NAME = 'movie826'
MONGO_DB_NAME = MONGO_NAME
MONGO_COLLECTION_NAME = MONGO_NAME

client = AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_CONNECTION_STRING]

'''
定义全局变量
'''
browser, context, page = None, None, None
HEADLESS = False

'''
定义信号量来控制并发量
'''
CONCURRENCY = 10
semaphore = asyncio.Semaphore(CONCURRENCY)

async def cancel_request(route, request):
    await route.abort()

async def scrape_page(page, url, selector):
    async with semaphore:
        logging.info('scraping %s', url)
        try:
            await page.route(re.compile(r"(\.png)|(\.jpg)"), cancel_request)
            await page.goto(url,  timeout=TIMEOUT * 1000)
            # await page.wait_for_load_state(state='networkidle')
            await page.wait_for_selector(selector)
            # return await page.content()
        except TimeoutError:
            logging.error('error occurred while scraping %s', url, exc_info=True)

async def scrape_index(page, index):
    url = INDEX_URL.format(index=index)
    await scrape_page(page, url, '.item .name')

async def parse_index(page):
    return await page.eval_on_selector_all('.item .name', 'nodes => nodes.map(node => node.href)')

async def scrape_detail(page, url):
    await scrape_page(page, url, 'h2')

async def parse_detail(page):
    try:
        url = page.url
        name = await page.locator('h2.m-b-sm').inner_text()
        categories = await page.locator('.categories button span').all_inner_texts()
        cover = await page.locator('.cover').get_attribute('src')
        score = await page.locator('.score').inner_text()
        drama = await page.locator('.drama p').inner_text()
        return {
            'url': url,
            'name': name,
            'categories': categories,
            'cover': cover,
            'score': score,
            'drama': drama
        }
    except AttributeError:
        logging.error('parse error,url: %s', url, exc_info=True)
        return None

# async def save_data(data):
#     name = data.get('name')
#     data_path = f'{RESULTS_DIR}/{name}.json'
#     json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

async def save_data(data):
    logging.debug('saving data %s', data)
    return await collection.update_one({
        'id': data.get('name')
    }, {
        '$set': data
    }, upsert=True)

async def run(index):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()
        await scrape_index(page, index)
        detail_urls = await parse_index(page)
        for detail_url in detail_urls:
            await scrape_detail(page, detail_url)
            detail_data = await parse_detail(page)
            await save_data(detail_data)

        await page.close()
        await context.close()
        await browser.close()

async def main():
    tasks =[]
    for index in range(1, TOTAL_PAGE + 1):
        task = asyncio.ensure_future(run(index))
        tasks.append(task)
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    end = time.time()
    logging.info('Cost time: %s', end - start)

