import random
from faker import Faker
import psycopg2
from datetime import datetime

# Configuração da conexão com o banco de dados

db = psycopg2.connect(
    host = 'localhost',
    user = 'postgres', 
    port = 5432,
    database = 'escola',
    password='1234',
    
)
cursor = db.cursor()

# Inicializa o Faker
faker = Faker("pt_BR")

# Função para gerar alunos
def gerar_alunos(qtd=40):
    alunos = []
    matriculas = set()  # Conjunto para garantir matrículas únicas
    cpfs = set()  # Conjunto para garantir CPFs únicos

    while len(alunos) < qtd:
        nome = faker.name()
        cpf = faker.cpf() 
        matricula = f"MAT{random.randint(100000, 999999)}"
        bairros = ["Centro", "Vila Nova", "Jardim", "São José", "São Francisco", "São Pedro"]
        cidades = ["Cidade A", "Cidade B"]
        
        # Garante que a matrícula seja única
        if matricula in matriculas:
            continue
        matriculas.add(matricula)

        if cpf in cpfs:
            continue
        cpfs.add(cpf)
        
        idade = random.randint(10, 18)
        rua = faker.street_name()
        bairro = random.choice(bairros)
        cidade = random.choice(cidades)
        nome_responsavel = faker.name()
        turma = f"Turma {random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
        alunos.append((nome, cpf, matricula, idade, rua, bairro, cidade, nome_responsavel, turma))
    return alunos

# Função para gerar disciplinas
def gerar_disciplinas(qtd=30):
    nomes_disciplinas = ['Matemática', 'Português', 'História', 'Geografia', 'Ciências', 
                   'Inglês', 'Educação Física', 'Artes', 'Filosofia', 'Sociologia',
                   'Física', 'Química', 'Biologia', 'Informática', 'Empreendedorismo']
    disciplinas_geradas = []
    for _ in range(qtd):
        disciplina = random.choice(nomes_disciplinas)
        professor = faker.name()
        periodo = random.choice(["Manha", "Tarde"])
        turma = f"Turma {random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
        disciplinas_geradas.append((disciplina, professor, periodo, turma))
    return disciplinas_geradas

def gerar_faltas(qtd=7000, alunos_ids=None, disciplinas_ids=None):
    faltas = []
    for _ in range(qtd):
        aluno_id = random.choice(alunos_ids)
        disciplina_id = random.choice(disciplinas_ids)
        start_date = datetime.strptime('2021-01-01', '%Y-%m-%d').date()
        end_date = datetime.strptime('2021-12-31', '%Y-%m-%d').date()

    # Gerar data aleatória
        data = faker.date_between(start_date=start_date, end_date=end_date)
        falta = random.choice(["Sim", "Nao"])
        faltas.append((aluno_id, disciplina_id, data, falta))
    return faltas

def obter_ids(tabela):
    cursor.execute(f"SELECT id FROM {tabela}")
    return [row[0] for row in cursor.fetchall()]


    

    



# Inserção no banco de dados
def inserir_dados():
    # Insere alunos
    alunos = gerar_alunos()
    cursor.executemany(
        "INSERT INTO Alunos (nome, cpf, matricula, idade, rua, bairro, cidade, nome_responsavel, turma)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        alunos
    )
    db.commit()

    # Insere disciplinas
    disciplinas = gerar_disciplinas()
    cursor.executemany(
        "INSERT INTO Disciplinas (nome, professor, periodo, turma) "
        "VALUES (%s, %s, %s, %s)",
        disciplinas
    )
    db.commit()

    alunos_ids = obter_ids("Alunos")
    disciplinas_ids = obter_ids("Disciplinas")

    faltas = gerar_faltas(qtd=7000, alunos_ids=alunos_ids, disciplinas_ids=disciplinas_ids)
    cursor.executemany(
    "INSERT INTO Faltas (aluno_id, disciplina_id, data, falta) "
    "VALUES (%s, %s, %s, %s)",
    faltas
    )
    db.commit()


def cadastrar_presenca():
    cursor.execute("SELECT id FROM Alunos")
    alunos_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM Disciplinas")
    disciplinas_ids = [row[0] for row in cursor.fetchall()]

    aluno_id = random.choice(alunos_ids)
    disciplina_id = random.choice(disciplinas_ids)
    #selecionar data aleatoria no ano de 2021
    start_date = datetime.strptime('2021-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2021-12-31', '%Y-%m-%d').date()

    # Gerar data aleatória
    data = faker.date_between(start_date=start_date, end_date=end_date)
    falta = random.choice(['Sim', 'Nao'])
    cursor.execute("INSERT INTO Faltas (aluno_id, disciplina_id, data, falta) VALUES (%s, %s, %s, %s)", (aluno_id, disciplina_id, data, falta))
    db.commit()

   

# Executa o script
if __name__ == "__main__":
    inserir_dados()
    print("Dados inseridos com sucesso!")
