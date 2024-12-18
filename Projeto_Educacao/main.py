import db_utils as dbu
from fastapi import FastAPI


app = FastAPI()

@app.get('/')
def root():
    return {'message': 'IDLE'}

@app.get('/presenca')
async def cadastrar_presenca():
    return dbu.cadastrar_presenca()

@app.get('/alunos')
async def listar_alunos():
    return dbu.consultar_alunos()

@app.get('/disciplinas')
async def listar_disciplinas():
    return dbu.consultar_disciplinas()

@app.get('/faltas')
async def listar_faltas():
    return dbu.consultar_faltas()

@app.get('/dias_letivos')
async def consultar_total_dias_letivos():
    return dbu.consultar_total_dias_letivos()

@app.get('/percentual_faltas_alunos')
async def consultar_percentual_faltas():
    return dbu.calcular_porcentagem_faltas_por_aluno()

@app.get('/percentual_faltas_disciplinas')
async def consultar_percentual_faltas_disciplinas():
    return dbu.calcular_porcentagem_faltas_por_disciplina()

@app.get('/deletar/faltas')
async def deletar_faltas():
    return dbu.deletar_faltas()
