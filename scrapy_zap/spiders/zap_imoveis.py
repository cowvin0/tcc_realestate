import scrapy
from pathlib import Path
from functools import reduce 
from  urllib.parse import urljoin

class ZapSpider(scrapy.Spider):

    name = 'zap'
    allowed_domains = ['www.zapimoveis.com.br']
    #start_urls = ['https://www.zapimoveis.com.br/venda/imoveis/rj+rio-de-janeiro']

    def __init__(self, cidade=None, *args, **kwargs):

        super(ZapSpider, self).__init__(*args, **kwargs)

        self.start_urls =[
                urljoin('https://www.zapimoveis.com.br/venda/imoveis',
                        cidade if cidade == None else 'rj+rio-de-janeiro/'),
                ]

    def parse(self, response):
        #tipo_imovel = input('Diga o tipo do imovel: ')
        #pagina_imovel = 'https://www.zapimoveis.com.br/venda/' + tipo_imovel + '/rj+rio-de-janeiro'
        selecionar_divs = response.css('div')
        coletando_hrefs = [href.css('a.result-card ::attr(href)').getall() for href in selecionar_divs]



        yield {'href': reduce(lambda x, y: x + y, coletando_hrefs)}

    def parse_imovel_info(self, response):
        pass
