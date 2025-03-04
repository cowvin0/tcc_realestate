from pydantic import BaseModel


class ModelStructure(BaseModel):
    academia: int
    area: float
    area_servico: float
    banheiro: int
    elevador: int
    espaco_gourmet: int
    portaria_24_horas: int
    piscina: int
    playground: int
    quadra_de_esporte: int
    quarto: int
    salao_de_festa: int
    sauna: int
    spa: int
    tipo: str
    vaga: int
    varanda_gourmet: int
    latitude: float
    longitude: float
    area_aluguel: float
    valor_aluguel: float
