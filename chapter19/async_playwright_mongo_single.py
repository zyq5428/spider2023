import logging
from os.path import exists
from os import makedirs
import json
import asyncio
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
MONGO_NAME = 'movie824'
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

async def scrape_page(url, selector):
    logging.info('scraping %s', url)
    try:
        await page.goto(url,  timeout=TIMEOUT * 1000)
        # await page.wait_for_load_state(state='networkidle')
        await page.wait_for_selector(selector)
        # return await page.content()
    except TimeoutError:
        logging.error('error occurred while scraping %s', url, exc_info=True)

async def scrape_index(index):
    url = INDEX_URL.format(index=index)
    await scrape_page(url, '.item .name')

async def parse_index():
    return await page.eval_on_selector_all('.item .name', 'nodes => nodes.map(node => node.href)')

async def scrape_detail(url):
    await scrape_page(url, 'h2')

async def parse_detail():
    url = page.url
    name = await page.eval_on_selector('h2', 'node => node.innerText')
    categories = await page.eval_on_selector_all('.categories button span', 'nodes => nodes.map(node => node.innerText)')
    cover = await page.eval_on_selector('.cover', 'node => node.src')
    score = await page.eval_on_selector('.score', 'node => node.innerText')
    drama = await page.eval_on_selector('.drama p', 'node => node.innerText')
    return {
        'url': url,
        'name': name,
        'categories': categories,
        'cover': cover,
        'score': score,
        'drama': drama
    }

# async def save_data(data):
#     name = data.get('name')
#     data_path = f'{RESULTS_DIR}/{name}.json'
#     json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

async def save_data(data):
    logging.info('saving data %s', data)
    return await collection.update_one({
        'id': data.get('name')
    }, {
        '$set': data
    }, upsert=True)

async def main():
    global browser, context, page
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            for index in range(1, TOTAL_PAGE + 1):
                await scrape_index(index)
                detail_urls = await parse_index()
                for detail_url in detail_urls:
                    await scrape_detail(detail_url)
                    detail_data = await parse_detail()
                    logging.info('data %s', detail_data)
                    await save_data(detail_data)
        finally:
            await page.close()
            await context.close()
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

