import scrapy
from pathlib import Path
from functools import reduce 
from  urllib.parse import urljoin
from scrapy.http import Request

class ZapSpider(scrapy.Spider):

    name = 'zap'
    allowed_domains = ['www.zapimoveis.com.br']
    start_urls = ['https://www.zapimoveis.com.br/venda/imoveis/rj+rio-de-janeiro/']

    def __init__(self, cidade=None, *args, **kwargs):

        super(ZapSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield Request(
            url=self.start_urls[0], 
            meta = {'dont_redirect': True,'handle_httpstatus_list': [302, 308]},
            callback=self.parse
            )

    def parse(self, response):
        selecionar_divs = response.css('div')
        coletando_hrefs = [href.css('a.result-card ::attr(href)').getall() for href in selecionar_divs]

        yield {'href': reduce(lambda x, y: x + y, coletando_hrefs)}

    def parse_imovel_info(self, response):
        pass
