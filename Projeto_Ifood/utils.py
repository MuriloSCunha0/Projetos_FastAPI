import csv 
import requests
from pydantic import BaseModel
import pandas as pd
import re
from typing import Optional, List


channels = 'channels.csv'
deliveries = 'deliveries.csv'
drivers = 'drivers.csv'
hubs = 'hubs.csv'
orders = 'orders.csv'
payments = 'payments.csv'
stores = 'stores.csv'


def carregar_lojas(stores):
    with open(stores, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Modelo de dados para a entrada
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

# Função para obter o nome do local usando Nominatim
def get_location_name(latitude: float, longitude: float) -> Optional[str]:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "MyFastAPIApp/1.0 (contact: murilosant976@gmail.com)"  # Substitua com um email válido
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    # Extrair o nome do local
    if "display_name" in data:
        return data["display_name"]
    else:
        return None

def save_store_locations_to_csv(stores: List[dict], filename: str):
    # Abre o arquivo para escrita
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["store_id", "store_name", "location_name"])
        writer.writeheader()

        for loja in stores:
            store_id = loja.get("store_id")
            store_name = loja.get("store_name")
            latitude = loja.get("store_latitude")
            longitude = loja.get("store_longitude")

            if latitude and longitude:
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)
                    location_name = get_location_name(latitude, longitude)
                except ValueError:
                    location_name = "Coordenadas inválidas"
            else:
                location_name = "Coordenadas ausentes"

            writer.writerow({
                "store_id": store_id,
                "store_name": store_name,
                "location_name": location_name
            })


def tratar_endereco(raw_address: str):
    # Caso o endereço esteja como "Coordenadas ausentes", retornamos valores nulos
    if raw_address == "Coordenadas ausentes":
        return {
            "street": None,
            "number": None,
            "neighborhood": None,
            "city": None,
            "state": None,
            "country": None,
            "zipcode": None
        }

    # Dividir o endereço em partes pela vírgula
    partes = [p.strip() for p in raw_address.split(",")]
    
    # Inicializando as variáveis do endereço
    endereco = {
        "street": None,
        "number": None,
        "neighborhood": None,
        "city": None,
        "state": None,
        "country": None,
        "zipcode": None
    }

    # Filtrar partes irrelevantes como "Região Geográfica" e "Região Metropolitana"
    partes_filtradas = [p for p in partes if not p.startswith("Região")]

    try:
        # Processar as partes significativas do endereço
        if len(partes_filtradas) >= 6:
            endereco["street"] = partes_filtradas[0]  # Rua ou local
            endereco["number"] = partes_filtradas[1] if partes_filtradas[1].isdigit() else None
            endereco["neighborhood"] = partes_filtradas[2]  # Bairro
            endereco["city"] = partes_filtradas[3]  # Cidade
            endereco["state"] = partes_filtradas[4]  # Estado
            endereco["zipcode"] = partes_filtradas[-2]  # Código postal
            endereco["country"] = partes_filtradas[-1]  # País
        else:
            print(f"Endereço mal formatado: {raw_address}")
    except Exception as e:
        print(f"Erro ao processar o endereço: {raw_address}. Erro: {e}")

    return endereco

def processar_csv(input_filename: str, output_filename: str):
    # Carregar o CSV com pandas
    df = pd.read_csv(input_filename)
    
    # Aplicar a função de tratamento ao campo 'location_name'
    df_tratado = df['location_name'].apply(tratar_endereco).apply(pd.Series)
    
    # Adicionar o 'store_id' e 'store_name' de volta ao DataFrame
    df_tratado['store_id'] = df['store_id']
    df_tratado['store_name'] = df['store_name']
    
    # Salvar o DataFrame tratado em um novo arquivo CSV
    df_tratado.to_csv(output_filename, index=False)
    print(f"Arquivo processado e salvo como {output_filename}")


processar_csv("Projeto_Ifood/store_locations.csv", "Projeto_Ifood/store_locations_tratado.csv")