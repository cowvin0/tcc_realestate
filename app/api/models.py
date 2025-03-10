from sqlalchemy import (
    Column,
    DECIMAL,
    String,
    DECIMAL,
    DECIMAL,
)
from app.api.database import Base


class Realestate(Base):
    __tablename__ = "imoveis_jp_scrape"

    id = Column(DECIMAL, primary_key=True, autoincrement=True)
    academia = Column(DECIMAL)
    area = Column(DECIMAL)
    area_servico = Column(DECIMAL)
    banheiro = Column(DECIMAL)
    condominio = Column(DECIMAL)
    elevador = Column(DECIMAL)
    endereco = Column(String(200))
    espaco_gourmet = Column(DECIMAL)
    iptu = Column(DECIMAL)
    piscina = Column(DECIMAL)
    playground = Column(DECIMAL)
    portaria_24_horas = Column(DECIMAL)
    quadra_de_esporte = Column(DECIMAL)
    quarto = Column(DECIMAL)
    salao_de_festa = Column(DECIMAL)
    sauna = Column(DECIMAL)
    spa = Column(DECIMAL)
    tipo = Column(String(40))
    vaga = Column(DECIMAL)
    valor = Column(DECIMAL)
    varanda_gourmet = Column(DECIMAL)
    latitude = Column(DECIMAL)
    longitude = Column(DECIMAL)
    bairro = Column(String(50))
    area_aluguel = Column(DECIMAL)
    valor_aluguel = Column(DECIMAL)
    qnt_beneficio = Column(DECIMAL)
