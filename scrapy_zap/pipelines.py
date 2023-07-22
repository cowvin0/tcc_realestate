# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapyZapPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        
        # Get the first elements of tuples:
        tups = ['area', 'banheiro', 'andar', 'condominio',
               'iptu', 'quarto', 'tipo', 'url', 'valor']
        for tup in tups:
            value = adapter.get(tup)[0]
            adapter[tup] = value
               

        #value = adapter.get('endereco')
        #value_without_newline = value.replace('\n', '').strip()
        #adapter['endereco'] = value_without_newline

        #dinheiro = adapter.get('valor')
        #dinheiro = dinheiro[0]
        #adapter['valor'] = dinheiro

        return item
