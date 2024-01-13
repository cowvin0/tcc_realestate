import scrapy
import os
import pandas as pd
import numpy as np
import time
import re
from scrapy_zap.items import ZapItem
from scrapy_playwright.page import PageMethod
from scrapy.http import Request


class VivaSpider(scrapy.Spider):
    name = "viva"
    allowed_domains = ["www.vivareal.com.br"]

    async def errback(self, failure):
        page = failure.request.meta['playwright_page']
        await page.closed()

    def __init__(self, *args, **kwargs):
        super(VivaSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        pass
