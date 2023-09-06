import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
                color_scheme='light',
                viewport={'width': 800, 'height': 600}
                )

        page = await context.new_page()

        await page.goto('https://www.zapimoveis.com.br/')

        city = page.locator('l-multiselect-491901')

        await city.fill('joao pessoa')

if __name__ == "__main__":
    asyncio.run(main())
    
