import asyncio
from playwright.async_api import Playwright, async_playwright

login_url = 'https://www.xn--pxtr7m.com/login'
username = '3072912320@qq.com'
password = '128314'
cookies_file = 'cookies_feiwen.txt'

headers = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

async def login_and_save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(login_url)
        await page.fill('input[name="email"]', username)
        await page.fill('input[name="password"]', password)
        input("请手动识别验证码点击登录，登录出界面后按回车键继续：")
        # await page.click('button[type="submit"]')
        # await page.locator("a.btn:has-text('贡献题头')").wait_for()
        cookies = await context.cookies()
        print(cookies)
        with open(cookies_file, 'w') as f:
            f.write(str(cookies))
        
        await context.close()
        await browser.close()

if __name__ == '__main__':
    asyncio.run(login_and_save_cookies())