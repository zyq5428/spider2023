import asyncio
from playwright.async_api import Playwright, async_playwright
import requests

login_url = 'https://www.xn--pxtr7m.com/login'
stories_url = 'https://www.xn--pxtr7m.com/threads/216723/profile'
email = '3072912320@qq.com'
password = '128314'

headers = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

async def login_and_save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(login_url)
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="password"]', password)
        input("请手动识别验证码点击登录，登录出界面后按回车键继续：")
        # await page.click('button[type="submit"]')
        # await page.locator("a.btn:has-text('贡献题头')").wait_for()
        await page.screenshot(path=f'screenshot-feiwen.png')
        cookies = await context.cookies()
        print(cookies)
        with open('cookies.txt', 'w') as f:
            f.write(str(cookies))
        await browser.close()

def use_saved_cookies():
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

    response = session.get(stories_url)

    print(session.cookies)
    print(session.cookies.get_dict())
    
    print(response.status_code)
    # print(response.text)

asyncio.run(login_and_save_cookies())
use_saved_cookies()