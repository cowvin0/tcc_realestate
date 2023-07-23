# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ZapItem(scrapy.Item):
    valor = scrapy.Field()
    tipo = scrapy.Field()
    endereco = scrapy.Field()
    condominio = scrapy.Field()
    iptu = scrapy.Field()
    area = scrapy.Field()
    quarto = scrapy.Field()
    banheiro = scrapy.Field()
    andar = scrapy.Field()
    academia = scrapy.Field()
    piscina = scrapy.Field()
    spa = scrapy.Field()
    quadra_de_esporte = scrapy.Field()
    elevador = scrapy.Field()
    sauna = scrapy.Field()
    varanda_gourmet = scrapy.Field()
    espaco_gourmet = scrapy.Field()
    playground = scrapy.Field()
    portaria_24_horas = scrapy.Field()
    area_servico = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
