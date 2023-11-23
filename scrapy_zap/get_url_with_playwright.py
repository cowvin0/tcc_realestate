import asyncio
import pandas as pd
import re
import os
from playwright.async_api import async_playwright

COND = os.environ.get("COND")
CITY = os.environ.get("CITY")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            color_scheme="light",
            user_agent="Mozilla (5.0)",
            viewport={"width": 1600, "height": 1000},
        )

        page = await context.new_page()

        list_type = [
            "apartamentos",
            "casas",
            "casas-de-condominio",
            "cobertura",
            "flat",
            "terrenos-lotes-condominios",
            "casa-comercial",
            "terrenos-lotes-comerciais",
        ]

        data_quant = {}

        type_url = {}

        for types in list_type:
            response = await page.goto(
                f"https://www.zapimoveis.com.br/{COND}/{types}/{CITY}"
            )

            if response.status != 404:
                await page.wait_for_timeout(5000)

                element = page.locator(
                    ".l-text.l-u-color-neutral-12.l-text--variant-heading-small.l-text--weight-semibold.undefined"
                )

                data_quant[types] = await element.text_content()

                await page.evaluate(
                    """
                                    var button = document.querySelectorAll(".l-button.l-button--context-primary.l-button--size-regular.l-button--icon-left");
                                    button[12].click();
                                    """
                )

                await page.wait_for_timeout(5000)

                url = await page.evaluate("window.location.href;")

                type_url[types + "_url"] = url[0:-1]

            else:
                print(f"Page does not exist: {response.status}")

        pattern = r"\d+\.\d+|\d+"

        data = {
            key: float(re.findall(pattern, val)[0].replace(".", ""))
            for key, val in data_quant.items()
        }

        data.update(type_url)

        data_df = pd.DataFrame(data, index=[0])

        data_df.to_csv("info.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main())
