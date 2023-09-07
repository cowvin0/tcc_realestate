import asyncio
import json
import re
import os
from playwright.async_api import async_playwright

#CITY = os.environ.get('CITY')

async def main():
    
    async with async_playwright() as p:
        
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
                color_scheme='light',
                user_agent='Mozilla (5.0)',
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
                            var button = document.querySelectorAll(".l-button.l-button--context-primary.l-button--size-regular.l-button--icon-left");
                            button[12].click();
                            ''')
        
        await page.wait_for_timeout(5000)

        url = await page.evaluate('window.location.href;')
        url = url.replace('terrenos-lotes-comerciais', 'apartamentos')[0:-1]

        data_json = json.dumps(data)

        os.environ['URL'] = url
        os.environ['QUANT'] = data_json

if __name__ == "__main__":
    asyncio.run(main())
