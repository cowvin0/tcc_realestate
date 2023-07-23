import re
from itemadapter import ItemAdapter


class ScrapyZapPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        
        # Get the first elements of tuples:
        tups = ['area', 'banheiro', 'andar', 'condominio',
                'iptu', 'quarto', 'tipo', 'url', 'valor',
                'endereco']
        for tup in tups:
            value = adapter.get(tup)[0]
            adapter[tup] = value
               
        # Converting não informado to np.nan
        nao_info = ['condominio', 'iptu']
        for nao in nao_info:
            value = adapter.get(nao)
            if value == 'não informado':
                adapter[nao] = None

        # Removing \n and empty space:
        not_in = ['condominio', 'iptu', 'url', 'id']
        fields = adapter.field_names()
        for field in fields:
            value = adapter.get(field)
            if value != None:
                if field not in not_in:
                    adapter[field] = value.replace('\n', '').strip()

        # Converting to float
        should_int = ['banheiro', 'condominio', 'area',
                      'valor', 'andar', 'iptu', 'quarto']
        for should in should_int:
            int_value = adapter.get(should)
            pattern = r'(?<!\S)(?:\d+(?:\.\d{3})*(?:,\d+)?)|\d+(?=\s*(?:m²|º|\b))'
            if int_value != None:
                value = re.findall(pattern, int_value)[0]
                adapter[should] = float(
                        value.replace('.', '').replace(', ', '')
                        )


        # Converting boolean features to 1
        boolean = ['academia', 'area_servico', 'espaco_gourmet',
                   'piscina', 'playground', 'portaria_24_horas',
                   'quadra_de_esporte', 'sauna', 'spa',
                   'varanda_gourmet', 'elevador']
        for does_exist in boolean:
            value = adapter.get(does_exist)
            if value != None:
                adapter[does_exist] = 1.0
        
        # Removing 'à venda'
        tipo_value = adapter.get('tipo')
        adapter['tipo'] = tipo_value.replace('à Venda', '').strip().lower().replace(' ', '_').replace(',', '') 

        return item
