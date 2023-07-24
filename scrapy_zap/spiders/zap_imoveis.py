import scrapy
import random
import re
from scrapy_zap.items import ZapItem
from functools import reduce 
from urllib.parse import urljoin
from scrapy.http import Request

class ZapSpider(scrapy.Spider):

    name = 'zap'
    allowed_domains = ['www.zapimoveis.com.br']
    #start_urls = ['https://www.zapimoveis.com.br/venda/imoveis/ma+sao-jose-de-ribamar/?transacao=venda&onde=,Maranh%C3%A3o,S%C3%A3o%20Jos%C3%A9%20de%20Ribamar,,,,,city,BR%3EMaranhao%3ENULL%3ESao%20Jose%20de%20Ribamar,-2.552398,-44.069254,&pagina=' + str(page) for page in range(1, 31)]
    start_urls = ['https://www.zapimoveis.com.br/venda/imoveis/ma+sao-jose-de-ribamar/?transacao=venda&onde=,Maranh%C3%A3o,S%C3%A3o%20Jos%C3%A9%20de%20Ribamar,,,,,city,BR%3EMaranhao%3ENULL%3ESao%20Jose%20de%20Ribamar,-2.552398,-44.069254,&pagina=1']

    def __init__(self, cidade=None, *args, **kwargs):
        super(ZapSpider, self).__init__(*args, **kwargs)

    def start_requests(self):

        for url in self.start_urls:
            yield Request(
                    url=url,#self.start_urls[0], 
                    meta = {'dont_redirect': True,
                            'handle_httpstatus_list': [302, 308]}, 
                    callback=self.parse
                    )
            
    def parse(self, response):

        selecionar_divs = response.css('div')
        coletando_hrefs = [href.css('a.result-card ::attr(href)').getall() for href in selecionar_divs]

        for url in reduce(lambda x, y: x + y, coletando_hrefs):
            yield response.follow(url, callback=self.parse_imovel_info,
                                  dont_filter = True
                                  )

    def parse_imovel_info(self, response):

        #def is_in(carac, info):
        #filtering = lambda values, info: [info if 'piscina' == info.replace('\n', '').lower().strip() else None for info in batata]    

        zap_item = ZapItem()

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
        url = response.url
        id = re.search(r'id-(\d+)/', url).group(1)

        filtering = lambda info: [check if info == check.replace('\n', '').lower().strip() else None for check in imovel_info]

        lista = {
                'academia': list(filter(lambda x: "academia" in x.lower(), imovel_info)),
                'piscina': list(filter(lambda x: x != None, filtering('piscina'))),
                'spa': list(filter(lambda x: x != None, filtering('spa'))),
                'sauna': list(filter(lambda x: "sauna" in x.lower(), imovel_info)),
                'varanda_gourmet': list(filter(lambda x: "varanda gourmet" in x.lower(), imovel_info)),
                'espaco_gourmet': list(filter(lambda x: "espaço gourmet" in x.lower(), imovel_info)),
                'quadra_de_esporte': list(filter(lambda x: 'quadra poliesportiva' in x.lower(), imovel_info)),
                'playground': list(filter(lambda x: "playground" in x.lower(), imovel_info)),
                'portaria_24_horas': list(filter(lambda x: "portaria 24h" in x.lower(), imovel_info)),
                'area_servico': list(filter(lambda x: "área de serviço" in x.lower(), imovel_info)),
                'elevador': list(filter(lambda x: "elevador" in x.lower(), imovel_info))
                }

        for info, conteudo in lista.items():
            if len(conteudo) == 0:
                zap_item[info] = None
            else:
                zap_item[info] = conteudo[0]

        zap_item['valor'] = preco_imovel,
        zap_item['tipo'] = tipo_imovel,
        zap_item['endereco'] = endereco_imovel.replace('\n', '').strip(),
        zap_item['condominio'] = condominio,
        zap_item['iptu'] = iptu,
        zap_item['area'] = area,
        zap_item['quarto'] = num_quarto,
        zap_item['banheiro'] = num_banheiro,
        zap_item['andar'] = andar,
        zap_item['url'] = response.url,
        zap_item['id'] = int(id)
        
        yield zap_item
