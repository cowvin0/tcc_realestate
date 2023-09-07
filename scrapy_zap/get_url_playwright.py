import asyncio
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

        await page.goto('https://www.zapimoveis.com.br/venda/imoveis/pb+joao-pessoa')

        await page.evaluate('document.querySelector(".l-multiselect__input-label").click()')

        await page.evaluate('''
                    (async () => {
                                
                        const types = document.querySelectorAll(".l-text.l-u-color-neutral-28.l-text--variant-body-regular.l-text--weight-regular.l-checkbox__label");
                        const button = document.querySelectorAll(".l-button.l-button--context-primary.l-button--size-regular.l-button--icon-left");
                        const data = {
                            "apartamento": types[2],
                            "casa": types[5],
                            "casa_condominio": types[7],
                            "flat": types[10],
                            "terreno_lote_condomio": types[12],
                            "casa_comercial": types[17],
                            "terreno_lote_comercial": types[21],
                            "cobertura": types[9]
                                      }

                        let previous_type = null;
                        for(const type in Object.entries(data)) {
                                    
                            var typeElement = type[1];
                                    
                            if(previous_type !== null) {
                                previous_type.click();
                                    }

                            button[12].click();
                            previous_type = typeElement;

                            await new Promise(resolve => setTimeout(resolve, 1000));
                                }
                            }
                        )();
                    ''')


        breakpoint()


if __name__ == "__main__":
    asyncio.run(main())
    
