import csv
import hashlib
from zipfile import ZipFile

# Função para calcular o hash SHA256 do CSV
def calcular_hash_csv(file_path: str) -> str:
    with open(file_path, "rb") as file:
        content = file.read()
    return hashlib.sha256(content).hexdigest()

# Função para compactar o arquivo CSV em ZIP
def compactar_csv(file_path: str, output_zip: str):
    with ZipFile(output_zip, "w") as zipf:
        zipf.write(file_path, arcname=file_path.split("/")[-1])

# Função para registrar logs
def registrar_log(mensagem: str, log_file: str = "logs.txt"):
    with open(log_file, "a") as file:
        file.write(f"{mensagem}\n")
