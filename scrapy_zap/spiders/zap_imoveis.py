import scrapy
import time
import random
import re
from scrapy.exceptions import CloseSpider
from scrapy_zap.items import ZapItem
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin
from scrapy.http import Request

class ZapSpider(scrapy.Spider):

    name = 'zap'
    allowed_domains = ['www.zapimoveis.com.br']
    start_urls = ['https://www.zapimoveis.com.br/venda/imoveis/pe+garanhuns/?transacao=venda&onde=,Pernambuco,Garanhuns,,,,,city,BR%3EPernambuco%3ENULL%3EGaranhuns,-8.89088,-36.496478,&pagina=']

    async def errback(self, failure): 
        page = failure.request.meta['playwright_page']
        await page.closed()

    def __init__(self, *args, **kwargs):
        super(ZapSpider, self).__init__(*args, **kwargs)

    def start_requests(self):

        page = 1
        while True:

            if page == 100:
                break

            yield Request(
                    url=self.start_urls[0] + str(page), 
                    meta = dict(
                        dont_redirect = True,
                        handle_httpstatus_list = [302, 308],
                        playwright = True,
                        playwright_include_page = True,
                        playwright_page_methods = {
                            'scroll_down': PageMethod('evaluate', r'''
                                                      (async () => {
                                                          const scrollStep = 10;
                                                          const delay = 16;
                                                          let currentPosition = 0;

                                                          function animateScroll() {
                                                              const pageHeight = Math.max(
                                                                  document.body.scrollHeight, document.documentElement.scrollHeight,
                                                                  document.body.offsetHeight, document.documentElement.offsetHeight,
                                                                  document.body.clientHeight, document.documentElement.clientHeight
                                                                  );

                                                              if (currentPosition < pageHeight) {
                                                                  currentPosition += scrollStep;
                                                                  if (currentPosition > pageHeight) {
                                                                      currentPosition = pageHeight;
                                                                  }
                                                                  window.scrollTo(0, currentPosition);
                                                                  requestAnimationFrame(animateScroll);
                                                                  }
                                                              }
                                                          animateScroll();
                                                          })();
                                                      '''),
                            'get_href': PageMethod('evaluate', 'Array.from(document.querySelectorAll("a.result-card")).map(a => a.href)'),
                            },
                        errback = self.errback
                        ),
                    callback=self.parse
                    )
            page += 1
            
    async def parse(self, response):

        page = response.meta['playwright_page']
        playwright_page_methods = response.meta['playwright_page_methods']

        #if response.status == 500:
        #    raise CloseSpider('It reaches to the 101 page, which is the limit')

        await page.evaluate(
                '''
                var intervalID = setInterval(function () {
                    var ScrollingElement = (document.scrollingElement || document.body);
                    scrollingElement.scrollTop += 20;
                    }, 100);
                '''
                )

        prev_height = None
        while True:
            curr_height = await page.evaluate('(window.innerHeight + window.scrollY)')
            if not prev_height:
                prev_height = curr_height
                time.sleep(1)
            elif prev_height == curr_height:
                await page.evaluate('clearInterval(intervalID)')
                break
            else:
                prev_height = curr_height
                time.sleep(1)

        hrefs = await page.evaluate('Array.from(document.querySelectorAll("a.result-card")).map(a => a.href)')

        await page.close()

        if len(hrefs) == 0:
            raise CloseSpider('No hrefs in response')
        for url in hrefs:
            yield response.follow(url, callback=self.parse_imovel_info,
                                  dont_filter = True
                                 )

    def parse_imovel_info(self, response):

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
        num_vaga = response.xpath('//ul[@class="feature__container info__base-amenities"]/li[@class="feature__item text-regular js-parking-spaces"]/span/text()').get()
        andar = response.xpath('//ul[@class="feature__container info__base-amenities"]/li').css('span[itemprop="floorLevel"]::text').get()
        url = response.url
        id = re.search(r'id-(\d+)/', url).group(1)

        filtering = lambda info: [check if info == check.replace('\n', '').lower().strip() else None for check in imovel_info]

        lista = {
                'salao_de_festa': list(filter(lambda x: "salão de festas" in x.lower(), imovel_info)),
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

        try:
            zap_item['endereco'] = endereco_imovel.replace('\n', '').strip(),
        except:
            zap_item['endereco'] = endereco_imovel,


        zap_item['valor'] = preco_imovel,
        zap_item['tipo'] = tipo_imovel,
        zap_item['condominio'] = condominio,
        zap_item['iptu'] = iptu,
        zap_item['area'] = area,
        zap_item['quarto'] = num_quarto,
        zap_item['vaga'] = num_vaga,
        zap_item['banheiro'] = num_banheiro,
        zap_item['andar'] = andar,
        zap_item['url'] = response.url,
        zap_item['id'] = int(id)
        
        yield zap_item
