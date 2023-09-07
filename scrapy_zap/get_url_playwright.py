import asyncio
import re
import os
from playwright.async_api import async_playwright

#CITY = os.environ.get('CITY')

async def main():
    
    async with async_playwright() as p:
        
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
                color_scheme='light',
                viewport={'width': 1600, 'height': 1000}
                )

        page = await context.new_page()

        data = {
                'apartamentos': 0,
                'casas': 0,
                'casas-de-condominio': 0,
                'cobertura': 0,
                'flat': 0,
                'terrenos-lotes-condominios': 0,
                'casa-comercial': 0,
                'terrenos-lotes-comerciais': 0
                }

        for types in data.keys():

            await page.goto(f'https://www.zapimoveis.com.br/venda/{types}/pb+joao-pessoa')

            await page.wait_for_timeout(5000)
            
            element = page.locator('.l-text.l-u-color-neutral-12.l-text--variant-heading-small.l-text--weight-semibold.undefined')

            data[types] = await element.text_content()

        pattern = r'\d+\.\d+|\d+'

        data = {key: float(re.findall(pattern, val)[0].replace('.', ''))  for key, val in data.items()}

        await page.evaluate('''
                            window.scroll({
                                top: 500,
                                behavior: 'smooth'
                                });
                            ''')

        breakpoint()


if __name__ == "__main__":
    asyncio.run(main())
