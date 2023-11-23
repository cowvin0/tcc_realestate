**Projeto para raspagem do ZapImóveis**

Instalar dependências: 

    ```
    poetry install
    ```

Entrar no ambiente: 

    ```
    poetry shell
    ``` 

Iniciar código de raspagem: 

    ```
    make scrape cond=aluguel_ou_venda city=nome_cidade 
    ```

Padrões de nome de cidades do ZapImóveis: 

    João Pessoa: pb+joao-pessoa 

    Boa Vista: rr+boa-vista 

    Maricá: rj+marica 

    Recife: pe+recife 

**Tarefas organizadas em ordem crescente de importância**

[x] Adicionar imagens e imóveis para aluguel no código da raspagem

[] Modelagem para todas as capitais do nordeste

[] Adicionar dados de raspagem raspagem numa API plumber

[] Shiny App
