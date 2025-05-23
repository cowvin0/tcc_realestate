import re
from unidecode import unidecode
from itemadapter import ItemAdapter


class ScrapyZapPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Get the first elements of tuples:
        tups = [
            "area",
            "banheiro",
            "andar",
            "condominio",
            "foto_imovel",
            "iptu",
            "quarto",
            "tipo",
            "url",
            "valor",
            "endereco",
            "vaga",
        ]
        for tup in tups:
            val = adapter.get(tup)
            if val != None:
                adapter[tup] = val[0]

        # Converting não informado to None
        nao_info = ["condominio", "iptu"]
        for nao in nao_info:
            value = adapter.get(nao)
            if value == "não informado":
                adapter[nao] = None

        # Removing \n and empty space:
        not_in = ["condominio", "iptu", "url", "id"]
        fields = adapter.field_names()
        for field in fields:
            value = adapter.get(field)
            if not isinstance(
                value, (int, type(None))
            ):  # value != None and type(value) != int:
                if field not in not_in:
                    adapter[field] = value.replace("\n", "").strip()

        # Converting to float
        should_int = [
            "banheiro",
            "condominio",
            "area",
            "valor",
            "andar",
            "iptu",
            "quarto",
            "vaga",
        ]
        for should in should_int:
            int_value = adapter.get(should)
            pattern = r"(?<!\S)(?:\d+(?:\.\d{3})*(?:,\d+)?)|\d+(?=\s*(?:m²|º|\b))"
            if int_value != None:
                value = re.findall(pattern, int_value)[0]
                adapter[should] = float(value.replace(".", "").replace(", ", ""))

        # Converting boolean features to 1
        boolean = [
            "academia",
            "area_servico",
            "espaco_gourmet",
            "piscina",
            "playground",
            "portaria_24_horas",
            "quadra_de_esporte",
            "sauna",
            "spa",
            "varanda_gourmet",
            "elevador",
            "salao_de_festa",
        ]
        for does_exist in boolean:
            value = adapter.get(does_exist)
            if value != None:
                adapter[does_exist] = 1.0

        # Removing 'à venda'
        tipo_value = adapter.get("tipo")
        if tipo_value != None:
            adapter["tipo"] = unidecode(
                (
                    tipo_value.replace("à Venda", "")
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace(",", "")
                )
            )

        # Removing dead keys from 'tipo'
        # tipo_value = adapter.get('tipo')
        # adapter['tipo'] = unidecode(tipo_value)

        # Inputing 0 in those boolean variables that aren't entirely falsy
        figure_it_out = [adapter.get(this) for this in boolean]
        dict_val = {k: v for (k, v) in zip(boolean, figure_it_out)}
        if any(figure_it_out):
            for name, value in dict_val.items():
                if value == None:
                    adapter[name] = 0

        return item
