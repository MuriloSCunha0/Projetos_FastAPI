import pandas as pd
import random
from datetime import datetime, timedelta

# Lista das principais capitais brasileiras e suas coordenadas (latitude, longitude)
capitais_brasil = {
    "São Paulo": (-23.55052, -46.633308),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Salvador": (-12.9714, -38.5014),
    "Brasília": (-15.7801, -47.9292),
    "Fortaleza": (-3.7172, -38.5437),
    "Belo Horizonte": (-19.9208, -43.9378),
    "Manaus": (-3.1190, -60.1969),
    "Curitiba": (-25.4284, -49.2733),
    "Recife": (-8.0476, -34.8770),
    "Porto Alegre": (-30.0277, -51.2287),
    "Belém": (-1.4558, -48.4902),
    "Goiânia": (-16.6869, -49.2648),
    "São Luís": (-2.5297, -44.3028),
    "Maceió": (-9.6658, -35.7350),
    "Natal": (-5.7945, -35.2110),
}

# Lista das principais cidades do interior do Brasil e suas coordenadas (latitude, longitude)
cidades_interior = {
    "Campinas": (-23.1857, -46.8978),
    "São José dos Campos": (-23.1896, -45.9009),
    "Ribeirão Preto": (-21.1771, -47.8103),
    "Uberlândia": (-18.9184, -48.2750),
    "Maringá": (-23.4200, -51.9333),
    "Sorocaba": (-23.5014, -47.4580),
    "Londrina": (-23.3045, -51.1691),
    "Juiz de Fora": (-21.7685, -43.3507),
    "Bauru": (-22.3141, -49.0605),
    "Cuiabá": (-15.6010, -56.0979),
    "Macapá": (0.0350, -51.0663),
    "Aracaju": (-10.9472, -37.0731),
    "São Bernardo do Campo": (-23.6896, -46.5647),
    "Volta Redonda": (-22.5247, -44.1006),
    "Divinópolis": (-20.1454, -44.8900),
}

# Adicionar as cidades do interior ao dicionário de capitais
capitais_brasil.update(cidades_interior)

# Função para gerar pedidos com entregas em capitais e cidades do interior
def gerar_pedidos(cidades, num_pedidos=100):
    pedidos = []
    centros_distribuicao = ['C1', 'C2', 'C3', 'C4', 'C5']  # IDs dos centros de distribuição
    start_date = datetime(2023, 1, 1)  # Data de início dos pedidos

    for i in range(num_pedidos):
        cidade = random.choice(list(cidades.keys()))  # Escolher aleatoriamente entre capital e cidade do interior
        coords = cidades[cidade]
        data_pedido = start_date + timedelta(days=i)  # Data de pedido incremental
        id_centro = random.choice(centros_distribuicao)  # Escolher aleatoriamente um centro de distribuição
        peso_total = random.randint(10, 500)  # Peso aleatório entre 10 e 500 kg
        valor_pedido = round(random.uniform(100, 5000), 2)  # Valor aleatório entre 100 e 5000 reais
        lucro = round(valor_pedido * random.uniform(0.2, 0.3), 2)  # Lucro aleatório (20-30% do valor do pedido)
        frete = round(random.uniform(20, 500), 2)  # Frete aleatório entre 20 e 500 reais

        pedido = {
            "ID_Pedido": f"P{i+1:04d}",  # Gerar ID do pedido como P0001, P0002, ...
            "Data_Pedido": data_pedido.strftime("%Y-%m-%d"),  # Formatar a data no formato YYYY-MM-DD
            "Local_Entrega_Latitude": coords[0],
            "Local_Entrega_Longitude": coords[1],
            "Peso_Total_kg": peso_total,
            "ID_Centro_Distribuicao": id_centro,
            "Valor_Pedido_R$": valor_pedido,
            "Lucro_R$": lucro,
            "Valor_Frete_R$": frete,
        }
        pedidos.append(pedido)
    
    return pd.DataFrame(pedidos)

# Gerar 200 pedidos para capitais e cidades do interior
pedidos_df = gerar_pedidos(capitais_brasil, num_pedidos=200)

# Salvar o DataFrame como um arquivo CSV
pedidos_df.to_csv("pedidos_atualizado.csv", index=False)

# Visualizar os primeiros pedidos gerados
print(pedidos_df.head())
