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
        condominio = response.xpath('//li[@class="price__item condominium color-dark text-regular"]/span/text()').get()
        iptu = response.xpath('//li[@class="price__item iptu color-dark text-regular"]/span/text()').get()
        area = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="floorSize"]::text').get()
        num_quarto = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="numberOfRooms"]::text').get()
        num_banheiro = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="numberOfBathroomsTotal"]::text').get()
        andar = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="floorLevel"]::text').get()
        
        yield {
                "valor": preco_imovel,
                "tipo": tipo_imovel,
                "endereco": endereco_imovel,
                "condominio": condominio,
                "iptu": iptu,
                "area": area,
                "quarto": num_quarto,
                "banheiro": num_banheiro,
                "andar": andar,
                "academia": list(filter(lambda x: "Academia" in x, imovel_info)),
                "piscina": list(filter(lambda x: "Piscina" in x, imovel_info)),
                "spa": list(filter(lambda x: "Spa" in x, imovel_info)),
                "sauna": list(filter(lambda x: "Sauna" in x, imovel_info)),
                "varanda_gourmet": list(filter(lambda x: "Varanda Gourmet" in x, imovel_info)),
                "espaco_gourmet": list(filter(lambda x: "Espaço Gourmet" in x, imovel_info)),
                "playground": list(filter(lambda x: "Playground" in x, imovel_info)),
                "portaria_24_horas": list(filter(lambda x: "Portaria 24h" in x, imovel_info)),
                "area_servico": list(filter(lambda x: "Área de serviço" in x, imovel_info)),
                "url": response.url
                }

    #@staticmethod
    #def info_isin(carac, info):

    #    if info in carac:
    #        return info
    #    else:
    #        None

