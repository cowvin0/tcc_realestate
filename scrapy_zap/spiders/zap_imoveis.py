import scrapy
from functools import reduce 
from urllib.parse import urljoin
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

        for url in reduce(lambda x, y: x + y, coletando_hrefs):
            yield response.follow(url, callback=self.parse_imovel_info)
            
            
        #yield {'href': reduce(lambda x, y: x + y, coletando_hrefs)}

    def parse_imovel_info(self, response):

        imovel_info = response.css('ul.amenities__list ::text').getall()
        tipo_imovel = response.css('a.breadcrumb__link--router ::text').get()
        endereco_imovel = response.css('span.link ::text').get()
        preco_imovel = response.xpath('//li[@class="price__item--main text-regular text-regular__bolder"]/strong/text()').get()
        condo_iptu = response.css('span.price__value ::text').getall()
        area = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="floorSize"]::text').get()
        num_quarto = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="numberOfRooms"]::text').get()
        num_banheiro = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="numberOfBathroomsTotal"]::text').get()
        andar = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="floorLevel"]::text').get()
        pass

