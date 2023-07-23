import numpy as np
import re
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
               
        # Converting None to np.nan
        select_all = adapter.field_names()
        for spe in select_all:
            value = adapter.get(spe)
            if value == np.nan:
                adapter[spe] = np.nan 

        # Converting não informado to np.nan
        nao_info = ['condominio', 'iptu']
        for nao in nao_info:
            value = adapter.get(nao)
            if value == 'não informado':
                adapter[nao] = np.nan

        # Removing \n and empty space:
        not_in = ['condominio', 'iptu', 'url', 'id']
        fields = adapter.field_names()
        for field in fields:
            value = adapter.get(field)
            if value != np.nan:
                if field not in not_in:
                    adapter[field] = value.replace('\n', '').strip()



        should_int = ['area', 'valor', 'quarto', 'banheiro' 
                      'condominio', 'iptu', 'andar']
        for should in should_int:
            int_value = adapter.get(should)
            pattern = r'(?<!\S)(?:\d+(?:\.\d{3})*(?:,\d+)?)|\d+(?=\s*(?:m²|º|\b))'
            if int_value != np.nan:
                value = re.findall(pattern, int_value)[0]
                adapter[should] = float(
                        value.replace('.', '').replace(',', '.')
                        )

        

        return item
