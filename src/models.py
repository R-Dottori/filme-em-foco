
from pydantic import BaseModel

class ModeloFilme(BaseModel):
    titulo: str
    titulo_original: str
    ano: int
    duracao: int
    diretor: str
    roteirista: str
    elenco: str
    nota: float
    num_votos: float
    sinopse: str
    genero: str
    verba: int
    receita: int
