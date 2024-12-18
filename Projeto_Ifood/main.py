from fastapi import FastAPI, HTTPException
from utils import carregar_lojas, get_location_name, save_store_locations_to_csv, processar_csv

app = FastAPI()
stores = 'stores.csv'
stores_locations = 'Projeto_Ifood\store_locations.csv'

@app.get('/root')
async def root():
    return {'message': 'Hello World'}

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

@app.get("/all-store-locations")
def get_all_store_locations():
    lojas = carregar_lojas(stores)
    resultados = []

    for loja in lojas:
        latitude = loja.get("store_latitude")
        longitude = loja.get("store_longitude")

        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                local_name = get_location_name(latitude, longitude)
                resultados.append({
                    "store_id": loja["store_id"],
                    "store_name": loja["store_name"],
                    "location_name": local_name
                })
            except ValueError:
                resultados.append({
                    "store_id": loja["store_id"],
                    "store_name": loja["store_name"],
                    "location_name": "Coordenadas inválidas"
                })
        else:
            resultados.append({
                "store_id": loja["store_id"],
                "store_name": loja["store_name"],
                "location_name": "Coordenadas ausentes"
            })

    return resultados

@app.get("/save-store-locations")
def save_store_locations():
    lojas = carregar_lojas(stores)
    save_store_locations_to_csv(lojas, "store_locations.csv")
    return {"message": "Localizações das lojas salvas com sucesso!"}

    
