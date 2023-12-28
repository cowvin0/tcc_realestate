import scrapy
import logging
import os
import json
import pandas as pd
import numpy as np
import time
import re
from scrapy_zap.items import ZapItem
from scrapy_playwright.page import PageMethod
from scrapy.http import Request


class ZapSpider(scrapy.Spider):
    name = 'zap'
    allowed_domains = ['www.zapimoveis.com.br']
    COND = os.environ.get('COND')
    CITY = os.environ.get('CITY')

    async def errback(self, failure):
        page = failure.request.meta['playwright_page']
        await page.closed()

    def __init__(self, *args, **kwargs):
        super(ZapSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.zapimoveis.com.br/{self.COND}/imoveis/{self.CITY}/']

    def start_requests(self):
        yield Request(
                url=self.start_urls[0],
                meta = dict(
                    dont_redirect=True,
                    handle_httpstatus_list = [302, 308],
                    playwright=True,
                    playwright_include_page = True,
                    playwright_page_methods = {
                        'types': PageMethod(
                            'evaluate',
                            r'''
                            var button_all = document.querySelector(".l-button.l-button--fluid.l-button--context-custom.l-button--size-large.l-button--icon-left.l-multiselect__input");
                            button_all.click();
                            '''
                            ),
                        
                        },
                    errback=self.errback
                    ),
                callback=self.parse,
                )

    async def parse(self, response):

        page = response.meta['playwright_page']
        playwright_page_methods = response.meta['playwright_page_methods']

        configs = await page.evaluate(r'''
                                      var types_element = document.querySelectorAll(".l-checkbox.l-checkbox--variant--regular");
                                      Array.from(types_element).map(a => a.textContent);
                                      '''
                                      )

        await page.wait_for_timeout(5000)

        house_types = [
            'Apartamento',
            'Casa de Condomínio',
            'Cobertura',
            'Flat',
            'Terreno / Lote / Condomínio',
            'Casa Comercial',
            'Casa',
            'Terrenos / Lotes Comerciais',
        ]

        pattern = r'\d+\.\d+|\d+'

        previous_type = 0

        for post_type in range(1, len(house_types)):

            previous_position_type = [i for i, v in enumerate(configs) if house_types[previous_type] in v]

            if len(previous_position_type):
                await page.evaluate(r'''
                                    types_element[{}].click();
                                    '''.format(previous_position_type[0])
                                    )

                await page.wait_for_timeout(5000)

                await page.evaluate(r'''
                                    var load_button = document.querySelectorAll(".l-button.l-button--context-primary.l-button--size-regular.l-button--icon-left");
                                    load_button[12].click();
                                    '''
                                    )

                await page.wait_for_timeout(6000)

                element_quant_specific = page.locator(
                    ".l-text.l-u-color-neutral-12.l-text--variant-heading-small.l-text--weight-semibold.undefined"
                )
                quant = await element_quant_specific.text_content()
                quant = float(re.findall(pattern, quant)[0].replace('.', ''))

                await page.wait_for_timeout(5000)

                url = await page.evaluate('window.location.href;')

                real_count = 1 if quant <= 100 else np.ceil(quant / 100) if quant <= 10000 else 100

                for pages in range(1, int(real_count) + 1):
                    yield Request(
                        url=url.replace('pagina=1', f'pagina={pages}'),
                        meta=dict(
                            dont_redirect=True,
                            handle_httpstatus_list=[302, 308],
                            playwright=True,
                            playwright_include_page=True,
                            playwright_page_methods={
                                'wait': PageMethod('evaluate', r'''
                                                   async function delay(ms) {
                                                       return new Promise(resolve => {
                                                           setTimeout(resolve, ms);
                                                        });
                                                       }
                                                   await delay(120 * 1000);
                                                   '''),
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
                            errback=self.errback
                        ),
                        callback=self.parse_desce_href
                    )

                await page.wait_for_timeout(5000)

                await page.evaluate(r'''
                                    types_element[{}].click();
                                    '''.format(previous_position_type)
                                    )

                await page.wait_for_timeout(5000)

                previous_type = post_type

    async def parse_desce_href(self, response):
        page = response.meta['playwright_page']
        playwright_page_methods = response.meta['playwright_page_methods']

        if response.status != 404:

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

            for url in hrefs:
                yield response.follow(url, callback=self.parse_imovel_info,
                                      dont_filter = True
                                     )


    
    def parse_imovel_info(self, response):

        zap_item = ZapItem()

        foto_imovel = response.xpath('//li[@class="js-carousel-item carousel__item"]//img/@src').get()
        imovel_info = response.css('ul.amenities__list ::text').getall()
        tipo_imovel = response.css('a.breadcrumb__link--router ::text').get()
        endereco_imovel = response.css('span.link ::text').get()
        preco_imovel = response.xpath('//li[@class="price__item--main text-regular text-regular__bolder"]/strong/text()').getall()#.get() if self.COND == "venda"
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
            zap_item['valor'] = preco_imovel[0] if self.COND == "venda" else preco_imovel[1],
        except:
            zap_item['valor'] = preco_imovel[0],

        zap_item['foto_imovel'] = foto_imovel,
        zap_item['endereco'] = endereco_imovel.replace('\n', '').strip() if endereco_imovel != None else val_ende[2].replace('\n', '').strip(),
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
