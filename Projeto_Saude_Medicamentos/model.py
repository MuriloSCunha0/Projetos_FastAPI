from pydantic import BaseModel
from datetime import datetime

class Medicamento(BaseModel):
    id: int
    nome: str
    categoria: str
    quantidade: int
    data_validade: datetime
