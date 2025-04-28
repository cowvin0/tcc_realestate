from pydantic import BaseModel
from typing import Optional


class ModelStructure(BaseModel):
    academia: Optional[int] = None
    area: Optional[float] = None
    area_servico: Optional[float] = None
    banheiro: Optional[int] = None
    elevador: Optional[int] = None
    espaco_gourmet: Optional[int] = None
    piscina: Optional[int] = None
    playground: Optional[int] = None
    portaria_24_horas: Optional[int] = None
    quadra_de_esporte: Optional[int] = None
    quarto: Optional[int] = None
    salao_de_festa: Optional[int] = None
    sauna: Optional[int] = None
    spa: Optional[int] = None
    tipo: Optional[str] = None
    vaga: Optional[int] = None
    varanda_gourmet: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_aluguel: Optional[float] = None
    valor_aluguel: Optional[float] = None
