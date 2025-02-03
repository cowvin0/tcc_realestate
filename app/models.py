from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DECIMAL,
)
from api.database import Base


class ListaRelatorios(Base):
    __tablename__ = "imoveis_jp_scrape"

    academia = Column(Boolean)
    area = Column(DECIMAL)
    area_servico = Column(Boolean)
    banheiro = Column(Integer)
    condominio = Column(DECIMAL)
    elevador = Column(Boolean)
    endereco = Column(String(200))
    espaco_gourmet = Column(Boolean)
    iptu = Column(DECIMAL)
    piscina = Column(Boolean)
    playground = Column(Boolean)
    portaria_24_horas = Column(Boolean)
    quadra_de_esporte = Column(Boolean)
    quarto = Column(Integer)
    salao_de_festa = Column(Boolean)
    sauna = Column(Boolean)
    spa = Column(Boolean)
    tipo = Column(String(25))
    vaga = Column(Integer)
    valor = Column(DECIMAL)
    varanda_gourmet = Column(Boolean)
    latitude = Column(DECIMAL)
    bairro = Column(String(50))
    area_aluguel = Column(DECIMAL)
    valor_aluguel = Column(DECIMAL)
    qnt_beneficio = Column(DECIMAL)
