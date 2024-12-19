import csv
import requests
from geopy.distance import geodesic
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from pydantic import BaseModel



channels = 'data\channels.csv'
deliveries = 'data\deliveries.csv'
drivers = 'data\drivers.csv'
hubs = 'data\hubs.csv'
orders = 'data\orders.csv'
payments = 'data\payments.csv'
stores = 'data\stores.csv'


def carregar_lojas(stores):
    with open(stores, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

def carregar_canais(channels):
    with open(channels, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

def carregar_entregas(deliveries):
    with open(deliveries, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

def carregar_motoristas(drivers):
    with open(drivers, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

def carregar_hubs(hubs):
    with open(hubs, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

def carregar_pedidos(orders):
    with open(orders, mode="r", encoding='latin1') as file:
        reader = csv.DictReader(file)
        return list(reader)

def carregar_pagamentos(payments):
    with open(payments, mode="r", encoding='latin1') as file:
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


def calcular_distancia(store_id1: int, store_id2: int, stores: str) -> Dict:
    lojas = carregar_lojas(stores)
    loja1 = next((l for l in lojas if int(l["store_id"]) == store_id1), None)
    loja2 = next((l for l in lojas if int(l["store_id"]) == store_id2), None)

    if not loja1 or not loja2:
        raise ValueError("Uma ou ambas as lojas não foram encontradas")
    
    coords1 = (float(loja1["store_latitude"]), float(loja1["store_longitude"]))
    coords2 = (float(loja2["store_latitude"]), float(loja2["store_longitude"]))
    distance = geodesic(coords1, coords2).kilometers
    return {"store_id1": store_id1, "store_id2": store_id2, "distance_km": distance}

def encontrar_lojas_proximas(latitude: float, longitude: float, top_n: int, stores: str) -> List[Dict]:
    lojas = carregar_lojas(stores)
    user_location = (latitude, longitude)
    distances = []

    for loja in lojas:
        try:
            store_location = (float(loja["store_latitude"]), float(loja["store_longitude"]))
            distance = geodesic(user_location, store_location).kilometers
            distances.append({"store_id": loja["store_id"], "store_name": loja["store_name"], "distance_km": distance})
        except ValueError:
            continue
    
    distances.sort(key=lambda x: x["distance_km"])
    return distances[:top_n]

def calcular_clusters(n_clusters: int, stores: str) -> List[Dict]:
    lojas = carregar_lojas(stores)
    coords = []
    store_info = []

    for loja in lojas:
        try:
            coords.append([float(loja["store_latitude"]), float(loja["store_longitude"])])
            store_info.append(loja)
        except ValueError:
            continue

    if len(coords) < n_clusters:
        raise ValueError("Número insuficiente de lojas para criar os clusters")

    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(coords)
    clusters = kmeans.labels_

    for i, loja in enumerate(store_info):
        loja["cluster"] = int(clusters[i])

    return [{"store_id": loja["store_id"], "store_name": loja["store_name"], "cluster": loja["cluster"]} for loja in store_info]


def estatisticas_de_distancia(stores: str) -> Dict:
    lojas = carregar_lojas(stores)
    coords = []

    for loja in lojas:
        try:
            coords.append((float(loja["store_latitude"]), float(loja["store_longitude"])))
        except ValueError:
            continue

    distances = [geodesic(c1, c2).kilometers for i, c1 in enumerate(coords) for c2 in coords[i + 1:]]
    return {
        "average_distance_km": np.mean(distances),
        "min_distance_km": np.min(distances),
        "max_distance_km": np.max(distances)
    }

def channel_analysis(filepath: str):
    df = pd.read_csv(filepath)
    channel_counts = df["channel_type"].value_counts()
    return {
        "total_channels": len(df),
        "channels_by_type": channel_counts.to_dict(),
    }

def delivery_statistics(filepath: str):
    df = pd.read_csv(filepath)
    delivered = df[df["delivery_status"] == "DELIVERED"]
    cancelled = df[df["delivery_status"] == "CANCELLED"]
    return {
        "total_deliveries": len(df),
        "average_distance_meters": delivered["delivery_distance_meters"].mean(),
        "delivered_count": len(delivered),
        "cancelled_count": len(cancelled),
    }

def driver_statistics(filepath: str):
    df = pd.read_csv(filepath)
    modal_counts = df["driver_modal"].value_counts()
    type_counts = df["driver_type"].value_counts()
    return {
        "total_drivers": len(df),
        "drivers_by_modal": modal_counts.to_dict(),
        "drivers_by_type": type_counts.to_dict(),
    }

def order_cancellation_rate(filepath: str):
    df = pd.read_csv(filepath)
    cancelled = len(df[df["order_status"] == "CANCELED"])
    finished = len(df[df["order_status"] == "FINISHED"])
    total = cancelled + finished
    return {
        "total_orders": len(df),
        "cancellation_rate": cancelled / total if total > 0 else 0,
    }

def average_ticket(filepath: str):
    df = pd.read_csv(filepath)
    finished = df[df["order_status"] == "FINISHED"]
    return {"average_ticket": finished["order_amount"].mean()}

def payment_statistics(filepath: str):
    df = pd.read_csv(filepath)
    payment_methods = df["payment_method"].value_counts()
    average_fee = df["payment_fee"].mean()
    return {
        "total_payments": len(df),
        "average_fee": average_fee,
        "payment_methods": payment_methods.to_dict(),
    }
    