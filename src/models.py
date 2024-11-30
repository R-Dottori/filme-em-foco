
from pydantic import BaseModel
from typing import Optional

class ModeloFilme(BaseModel):
    titulo: str
    titulo_original: Optional[str] = ''
    ano: int
    duracao: Optional[int] = 0
    diretor: Optional[str] = ''
    roteirista: Optional[str] = ''
    elenco: Optional[str] = ''
    nota: Optional[float] = 0.0
    num_votos: Optional[float] = 0.0
    sinopse: Optional[str] = ''
    genero: Optional[str] = ''
    verba: Optional[int] = 0
    receita: Optional[int] = 0
    analises: Optional[str] = ''

# NOVO MODELO
# OPINIÃO A SER RESUMIDA OU CATEGORIZADA
class ModeloAnalise(BaseModel):
    analise: str
