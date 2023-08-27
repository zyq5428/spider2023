import asyncio
from playwright.async_api import Playwright, async_playwright
import requests

async def login_and_save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.xn--pxtr7m.com/login')
        await page.fill('input[name="email"]', '3072912320@qq.com')
        await page.fill('input[name="password"]', '128314')
        input("请手动识别验证码，识别正确后按回车键继续：")
        # await page.click('button[type="submit"]')
        # await page.locator("a.btn:has-text('贡献题头')").wait_for()
        # await page.locator("a.btn", name="贡献题头").wait_for()
        await page.screenshot(path=f'screenshot-feiwen.png')
        cookies = await context.cookies()
        print(cookies)
        with open('cookies.txt', 'w') as f:
            f.write(str(cookies))
        await browser.close()

def use_saved_cookies():
    url = 'https://www.xn--pxtr7m.com/threads/216723/profile'
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    jar = requests.cookies.RequestsCookieJar()
    session = requests.session()
    session.headers = headers
    with open('cookies.txt', 'r') as f:
        cookies = eval(f.read())
    for cookie in cookies:
        print(cookie)
        # session.cookies.set(cookie['name'], cookie['value'])
        jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
    session.cookies.update(jar)
    print(session.cookies.get_dict())
    # response = session.get(url, cookies=jar, headers=headers)
    response = session.get(url)
    print(session.cookies)
    print(session.cookies.get_dict())
    print(response.status_code)
    # print(response.text)

asyncio.run(login_and_save_cookies())
use_saved_cookies()