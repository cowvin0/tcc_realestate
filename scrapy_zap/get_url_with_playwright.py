import asyncio
import random
import pandas as pd
import re
import os
from playwright.async_api import async_playwright

COND = os.environ.get("COND")
CITY = os.environ.get("CITY")


proxy_pool = [
    {"server": "200.166.248.217:128"},
    {"server": "177.69.118.177:8080"},
    {"server": "191.243.46.2:18283"},
    {"server": "187.73.102.70:9292"},
    {"server": "170.83.200.138:3128"},
    {"server": "138.59.20.42:9999"},
    {"server": "168.228.36.22:27234"},
    {"server": "187.19.166.107:20183"},
    {"server": "187.1.57.206:20183"},
]


async def main():
    # proxy = random.choice(proxy_pool)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            # proxy=proxy
        )

        context = await browser.new_context(
            color_scheme="light",
            user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0;",
            viewport={"width": 1600, "height": 1000},
        )

        page = await context.new_page()

        list_type = [
            "casas-de-condominio",
            "cobertura",
            "apartamentos",
            "casas",
            "terrenos-lotes-condominios",
            "flat",
            "terrenos-lotes-comerciais",
            "casa-comercial",
        ]

        data_quant = {}

        type_url = {}

        for types in list_type:
            response = await page.goto(
                f"https://www.zapimoveis.com.br/{COND}/{types}/{CITY}"
            )

            if response.status != 404:
                await page.wait_for_timeout(5000)

                await page.evaluate(
                    """
                    var button = document.querySelectorAll(".l-button.l-button--context-primary.l-button--size-regular.l-button--icon-left");
                    button[12].click();
                    """
                )

                element = page.locator(
                    ".l-text.l-u-color-neutral-12.l-text--variant-heading-small.l-text--weight-semibold.undefined"
                )

                data_quant[types] = await element.text_content()

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
