import psycopg2 
import random
from faker import Faker

db = psycopg2.connect(
    host = 'localhost',
    user = 'postgres', 
    port = '5432',
    database = 'escola',
    password='1234'
)
cursor = db.cursor()
def cadastrar_presenca(qtn = 2000):
    for _ in range(qtn):
        cursor.execute("SELECT id FROM Alunos")
        alunos_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM Disciplinas")
        disciplinas_ids = [row[0] for row in cursor.fetchall()]

        aluno_id = random.choice(alunos_ids)
        disciplina_id = random.choice(disciplinas_ids)
        data = faker.date()
        falta = random.choice(['Nao', 'Sim'])
        cursor.execute("INSERT INTO Faltas (aluno_id, disciplina_id, data, falta) VALUES (%s, %s, %s, %s)", (aluno_id, disciplina_id, data, falta))
        db.commit()
    return {"message": "Presença cadastrada com sucesso!"}

faker = Faker("pt_BR")

def consultar_alunos():
    cursor.execute('SELECT * FROM alunos')
    alunos = cursor.fetchall()
    return alunos

def consultar_disciplinas():
    cursor.execute('SELECT * FROM disciplinas')
    disciplinas = cursor.fetchall()
    return disciplinas

def consultar_faltas():
    cursor.execute('SELECT * FROM faltas')
    faltas = cursor.fetchall()
    return faltas

def consultar_total_dias_letivos():
    cursor.execute('SELECT COUNT(DISTINCT data) FROM faltas')
    total_dias = cursor.fetchone()
    return total_dias[0] if total_dias else 0


def calcular_porcentagem_faltas_por_aluno():
    # Consultar dados necessários
    alunos = consultar_alunos()
    faltas = consultar_faltas()

    # Criar dicionários para armazenar total de faltas e presenças por aluno
    total_faltas_por_aluno = {}
    total_presencas_por_aluno = {}
    nomes_alunos = {}

    # Inicializar contadores para cada aluno
    for aluno in alunos:
        aluno_id = aluno[0]  # Considerando que o primeiro campo é o ID do aluno
        nome_aluno = aluno[1]  # Considerando que o segundo campo é o nome do aluno
        total_faltas_por_aluno[aluno_id] = 0
        total_presencas_por_aluno[aluno_id] = 0
        nomes_alunos[aluno_id] = nome_aluno

    # Processar dados da tabela de faltas
    for falta in faltas:
        aluno_id = falta[1]  # Considerando que o segundo campo é o aluno_id
        foi_falta = falta[4].lower() == 'sim'  # Considerando que o quarto campo é "falta"

        if aluno_id in total_faltas_por_aluno:
            if foi_falta:
                total_faltas_por_aluno[aluno_id] += 1
            else:
                total_presencas_por_aluno[aluno_id] += 1

    # Calcular porcentagem de faltas por aluno
    porcentagem_faltas = []
    for aluno_id in total_faltas_por_aluno:
        total_faltas = total_faltas_por_aluno[aluno_id]
        total_presencas = total_presencas_por_aluno[aluno_id]
        total_aulas = total_faltas + total_presencas

        if total_aulas > 0:
            porcentagem = (total_faltas / total_aulas) * 100
        else:
            porcentagem = 0.0

        porcentagem_faltas.append({
            "aluno_id": aluno_id,
            "nome": nomes_alunos[aluno_id],
            "porcentagem_faltas": porcentagem
        })

    return porcentagem_faltas

def calcular_porcentagem_faltas_por_disciplina():
    # Consultar dados necessários
    disciplinas = consultar_disciplinas()
    faltas = consultar_faltas()

    # Criar dicionários para armazenar total de faltas e presenças por disciplina
    total_faltas_por_disciplina = {}
    total_presencas_por_disciplina = {}
    nomes_disciplinas = {}
    nomes_professores = {}

    # Inicializar contadores para cada disciplina
    for disciplina in disciplinas:
        disciplina_id = disciplina[0]  # Considerando que o primeiro campo é o ID da disciplina
        nome_disciplina = disciplina[1]  # Considerando que o segundo campo é o nome da disciplina
        nomes_professor = disciplina[2]  # Considerando que o terceiro campo é o nome do professor
        total_faltas_por_disciplina[disciplina_id] = 0
        total_presencas_por_disciplina[disciplina_id] = 0
        nomes_disciplinas[disciplina_id] = nome_disciplina
        nomes_professores[disciplina_id] = nomes_professor


    # Processar dados da tabela de faltas
    for falta in faltas:
        disciplina_id = falta[2]  # Considerando que o terceiro campo é o disciplina_id
        foi_falta = falta[4].lower() == 'sim'  # Considerando que o quarto campo é "falta"

        if disciplina_id in total_faltas_por_disciplina:
            if foi_falta:
                total_faltas_por_disciplina[disciplina_id] += 1
            else:
                total_presencas_por_disciplina[disciplina_id] += 1

    # Calcular porcentagem de faltas por disciplina
    porcentagem_faltas = []
    for disciplina_id in total_faltas_por_disciplina:
        total_faltas = total_faltas_por_disciplina[disciplina_id]
        total_presencas = total_presencas_por_disciplina[disciplina_id]
        total_aulas = total_faltas + total_presencas

        if total_aulas > 0:
            porcentagem = (total_faltas / total_aulas) * 100
        else:
            porcentagem = 0.0

        porcentagem_faltas.append({
            "disciplina_id": disciplina_id,
            "nome": nomes_disciplinas[disciplina_id],
            "nome_professor":nomes_professores[disciplina_id],
            "porcentagem_faltas": porcentagem
        })
    
    return porcentagem_faltas



    


