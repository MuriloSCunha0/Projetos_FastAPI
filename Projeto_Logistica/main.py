from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Caminhos dos arquivos CSV
BASE_PATH = "data/"
PONTOS_FILE = f"{BASE_PATH}pontos_entrega_geograficos.csv"
ROTAS_FILE = f"{BASE_PATH}rotas_otimizadas.csv"
DISTANCIAS_FILE = f"{BASE_PATH}matriz_distancias.csv"

# Rotas da API
@app.get("/")
def root():
    return {"message": "API de Otimização de Rotas em Funcionamento"}

@app.get("/pontos")
def get_pontos():
    """Retorna todos os pontos de entrega"""
    try:
        pontos_df = pd.read_csv(PONTOS_FILE)
        return pontos_df.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": "Arquivo de pontos não encontrado"}

@app.get("/rotas")
def get_rotas():
    """Retorna as rotas otimizadas"""
    try:
        rotas_df = pd.read_csv(ROTAS_FILE)
        return rotas_df.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": "Arquivo de rotas não encontrado"}

@app.get("/distancias")
def get_distancias():
    """Retorna a matriz de distâncias"""
    try:
        distancias_df = pd.read_csv(DISTANCIAS_FILE)
        return distancias_df.to_dict()
    except FileNotFoundError:
        return {"error": "Arquivo de distâncias não encontrado"}

@app.get("/rota-veiculo/{veiculo_id}")
def get_rota_veiculo(veiculo_id: int):
    """Retorna a rota de um veículo específico"""
    try:
        rotas_df = pd.read_csv(ROTAS_FILE)
        rota = rotas_df[rotas_df["Veículo"] == veiculo_id]
        if rota.empty:
            return {"error": f"Nenhuma rota encontrada para o veículo {veiculo_id}"}
        return rota.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": "Arquivo de rotas não encontrado"}

@app.get("/rotas-veiculos")
def get_rotas_veiculos():
    """Retorna as rotas otimizadas com veículos e seus custos"""
    try:
        rotas_df = pd.read_csv(r"data\rotas_otimizadas.csv")
        return rotas_df.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": "Arquivo de rotas não encontrado"}
