from fastapi import FastAPI, HTTPException
from utils import (
    carregar_lojas, 
    get_location_name, 
    save_store_locations_to_csv, 
    processar_csv, 
    calcular_distancia, 
    encontrar_lojas_proximas, 
    calcular_clusters, 
    estatisticas_de_distancia,
    channel_analysis,
    delivery_statistics,
    driver_statistics,
    order_cancellation_rate,
    average_ticket,
    payment_statistics,
)

app = FastAPI()
stores = 'data\stores.csv'

@app.get('/root')
async def root():
    return {'message': 'Hello World'}

@app.get("/load-stores")
async def load_stores():
    carregar_lojas(stores)

@app.get("/store-location/{store_id}")
def get_store_location(store_id: int):
    lojas = carregar_lojas(stores)
    loja = next((l for l in lojas if int(l["store_id"]) == store_id), None)

    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    latitude = loja.get("store_latitude")
    longitude = loja.get("store_longitude")

    if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            local_name = get_location_name(latitude, longitude)
            return {"store_id": store_id, "store_name": loja["store_name"], "location_name": local_name}
        except ValueError:
            raise HTTPException(status_code=400, detail="Coordenadas inválidas para a loja")
    else:
        raise HTTPException(status_code=400, detail="Coordenadas ausentes para a loja")

@app.get("/distance-between-stores/{store_id1}/{store_id2}")
def distance_between_stores(store_id1: int, store_id2: int):
    return calcular_distancia(store_id1, store_id2, stores)

@app.get("/nearest-stores")
def nearest_stores(latitude: float, longitude: float, top_n: int = 5):
    return encontrar_lojas_proximas(latitude, longitude, top_n, stores)

@app.get("/store-clusters")
def store_clusters(n_clusters: int = 3):
    return calcular_clusters(n_clusters, stores)



@app.get("/distance-statistics")
def distance_statistics():
    return estatisticas_de_distancia(stores)

@app.get("/channel-analysis")
def get_channel_analysis():
    return channel_analysis("data/channels.csv")

@app.get("/delivery-statistics")
def get_delivery_statistics():
    return delivery_statistics("data/deliveries.csv")

@app.get("/driver-statistics")
def get_driver_statistics():
    return driver_statistics("data/drivers.csv")


@app.get("/order-cancellation-rate")
def get_order_cancellation_rate():
    return order_cancellation_rate("data/orders.csv")

@app.get("/average-ticket")
def get_average_ticket():
    return average_ticket("data/orders.csv")

@app.get("/payment-statistics")
def get_payment_statistics():
    return payment_statistics("data/payments.csv")
