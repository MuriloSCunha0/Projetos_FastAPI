from fastapi import FastAPI, HTTPException
from model import Medicamento
from utils import calcular_hash_csv, compactar_csv, registrar_log
import csv
from datetime import datetime, timedelta

app = FastAPI()
CSV_FILE = "medicamentos.csv"

# Função auxiliar para carregar medicamentos
def carregar_medicamentos():
    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        return []

# Função auxiliar para salvar medicamentos
def salvar_medicamentos(medicamentos):
    with open(CSV_FILE, mode="w", newline="") as file:
        fieldnames = ["id", "nome", "categoria", "quantidade", "data_validade"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(medicamentos)

@app.post("/medicamentos/")
def cadastrar_medicamento(medicamento: Medicamento):
    medicamentos = carregar_medicamentos()
    medicamentos.append(medicamento.dict())
    salvar_medicamentos(medicamentos)
    registrar_log(f"Medicamento {medicamento.nome} cadastrado com sucesso.")
    return {"mensagem": "Medicamento cadastrado com sucesso."}

@app.get("/medicamentos/")
def listar_medicamentos():
    return carregar_medicamentos()

@app.get("/medicamentos/em_falta")
def medicamentos_em_falta():
    medicamentos = carregar_medicamentos()
    em_falta = [med for med in medicamentos if int(med["quantidade"]) < 5]
    return em_falta

@app.get("/medicamentos/validade_proxima")
def validade_proxima():
    hoje = datetime.now()
    limite = hoje + timedelta(days=30)
    medicamentos = carregar_medicamentos()
    proximos = [
        med for med in medicamentos 
        if datetime.strptime(med["data_validade"], "%Y-%m-%d") < limite
    ]                    
    return proximos

@app.put("/medicamentos/{id}")
def atualizar_medicamento(id: int, medicamento: Medicamento):
    medicamentos = carregar_medicamentos()
    for med in medicamentos:
        if int(med["id"]) == id:
            med.update(medicamento.dict())
            salvar_medicamentos(medicamentos)
            registrar_log(f"Medicamento {id} atualizado com sucesso.")
            return {"mensagem": "Medicamento atualizado com sucesso."}
    raise HTTPException(status_code=404, detail="Medicamento não encontrado.")

@app.delete("/medicamentos/{id}")
def excluir_medicamento(id: int):
    medicamentos = carregar_medicamentos()
    medicamentos = [med for med in medicamentos if int(med["id"]) != id]
    salvar_medicamentos(medicamentos)
    registrar_log(f"Medicamento {id} excluído com sucesso.")
    return {"mensagem": "Medicamento excluído com sucesso."}

@app.get("/medicamentos/quantidade")
def quantidade_medicamentos():
    medicamentos = carregar_medicamentos()
    return {"quantidade": len(medicamentos)}

@app.get("/medicamentos/compactar")
def compactar_medicamentos():
    output_zip = "medicamentos.zip"
    compactar_csv(CSV_FILE, output_zip)
    registrar_log("Arquivo CSV compactado.")
    return {"mensagem": f"Arquivo compactado disponível: {output_zip}"}

@app.get("/medicamentos/hash")
def hash_medicamentos():
    hash_csv = calcular_hash_csv(CSV_FILE)
    registrar_log("Hash SHA256 do arquivo gerado.")
    return {"hash_sha256": hash_csv}
