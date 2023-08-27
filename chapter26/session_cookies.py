import asyncio
from playwright.async_api import Playwright, async_playwright
import requests

async def login_and_save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://login2.scrape.center/')
        await page.fill('input[name="username"]', 'admin')
        await page.fill('input[name="password"]', 'admin')
        await page.click('input[type="submit"]')
        cookies = await context.cookies()
        with open('cookies.txt', 'w') as f:
            f.write(str(cookies))
        await browser.close()

def use_saved_cookies():
    session = requests.session()
    with open('cookies.txt', 'r') as f:
        cookies = eval(f.read())
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    response = session.get('https://login2.scrape.center/page/1')
    # print(response.text)
    print(session.cookies.get_dict())

asyncio.run(login_and_save_cookies())
use_saved_cookies()