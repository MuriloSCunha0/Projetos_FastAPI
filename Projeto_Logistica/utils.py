from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from geopy.distance import geodesic
import pandas as pd
import numpy as np

# Carregar as bases de dados criadas anteriormente
pedidos_df = pd.read_csv(r"Projeto_Logistica\data\pedidos_atualizado.csv")
caminhoes_df = pd.read_csv(r"Projeto_Logistica\data\caminhoes.csv")
centros_df = pd.read_csv(r"Projeto_Logistica\data\centros_distribuicao.csv")

# Criar matriz de distâncias baseada na localização geográfica (pedidos e centros de distribuição)
def calculate_distance_matrix(locations):
    coords = locations[["Latitude", "Longitude"]].values
    num_points = len(coords)
    distance_matrix = np.zeros((num_points, num_points))

    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                distance_matrix[i][j] = geodesic(coords[i], coords[j]).kilometers
    return distance_matrix

# Criar o DataFrame de localizações combinando centros e pontos de entrega
loc_centros = centros_df[["ID_Centro", "Localizacao_Latitude", "Localizacao_Longitude"]].rename(
    columns={"Localizacao_Latitude": "Latitude", "Localizacao_Longitude": "Longitude"}
)
loc_pedidos = pedidos_df[["ID_Pedido", "Local_Entrega_Latitude", "Local_Entrega_Longitude"]].rename(
    columns={"Local_Entrega_Latitude": "Latitude", "Local_Entrega_Longitude": "Longitude"}
)
locations = pd.concat([loc_centros, loc_pedidos], ignore_index=True)

# Criar a matriz de distâncias
distance_matrix = calculate_distance_matrix(locations)

# Modelo de dados para o roteamento
def create_data_model():
    data = {
        "distance_matrix": distance_matrix,
        "num_vehicles": len(caminhoes_df),
        "depot": 0,  # Primeiro centro de distribuição como depósito
        "capacities": (np.round(caminhoes_df["Capacidade_Peso_kg"] * 0.75)).astype(int).tolist(),  # Garantir que não ultrapasse 75% da capacidade
        "costs": caminhoes_df["Custo_por_Km_R$"].tolist(),
        "speeds": caminhoes_df["Velocidade_Media_Km_h"].tolist(),
    }
    return data

# Função para calcular o custo da distância
def distance_callback(from_index, to_index, manager):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return int(distance_matrix[from_node][to_node] * 1000)  # Distância em metros

# Resolver o problema de roteamento
def solve_routing(data):
    manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], data["depot"])
    routing = pywrapcp.RoutingModel(manager)

    # Registrar a callback de distância
    transit_callback_index = routing.RegisterTransitCallback(
        lambda from_index, to_index: distance_callback(from_index, to_index, manager)
    )
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Restrições de capacidade
    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        if node < len(centros_df):  # Centro de distribuição
            return 0
        return pedidos_df.iloc[node - len(centros_df)]["Peso_Total_kg"]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, data["capacities"], True, "Capacity"
    )

    # Restrições de tempo
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        vehicle_index = manager.VehicleIndexFromNode(from_index)
        distance_km = distance_matrix[from_node][to_node]
        return int(distance_km / data["speeds"][vehicle_index] * 60)  # Tempo em minutos

    time_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.AddDimension(
        time_callback_index, 0, 9 * 60, True, "Time"  # 9 horas em minutos
    )

    # Estratégia de busca
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        return extract_solution(manager, routing, solution, data)
    else:
        raise Exception("Nenhuma solução encontrada.")

def extract_solution(manager, routing, solution, data):
    routes = []
    route_id = 1  # ID de identificação das rotas
    for vehicle_id in range(routing.vehicles()):
        index = routing.Start(vehicle_id)
        route = []
        total_cost = 0
        total_time = 0
        total_weight = 0
        pedidos_entregues = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            if node_index >= len(centros_df):  # Se for um pedido
                pedido_id = pedidos_df.iloc[node_index - len(centros_df)]["ID_Pedido"]
                pedidos_entregues.append(pedido_id)
                total_weight += pedidos_df.iloc[node_index - len(centros_df)]["Peso_Total_kg"]
            next_index = solution.Value(routing.NextVar(index))
            if not routing.IsEnd(next_index):
                next_node_index = manager.IndexToNode(next_index)
                # Distância e tempo para o próximo nó
                distance_km = distance_matrix[node_index][next_node_index]
                cost = distance_km * data["costs"][vehicle_id]
                time = distance_km / data["speeds"][vehicle_id]
                total_cost += cost
                total_time += time
            index = next_index
        # Adicionar a rota apenas se ela tiver mais de um ponto visitado (exclui rotas inúteis)
        if len(route) > 1 and total_weight <= data["capacities"][vehicle_id]:
            routes.append(
                {
                    "Rota_ID": route_id,
                    "Veículo": vehicle_id,
                    "Rota": route,
                    "Pedidos_Entregues": pedidos_entregues,
                    "Custo_Total_R$": round(total_cost, 2),
                    "Tempo_Total_h": round(total_time, 2),
                    "Tempo_Total_dias": round(total_time / 9 / 60, 2),  # Tempo em dias
                }
            )
            route_id += 1
    return routes

# Criar modelo de dados e resolver o problema
data = create_data_model()
routes = solve_routing(data)

# Criar DataFrame com os resultados das rotas
routes_df = pd.DataFrame(routes)

# Salvar os resultados finais
routes_df.to_csv("rotas_otimizadas_com_pedidos.csv", index=False)

# Exibir as primeiras linhas do DataFrame com as rotas otimizadas
routes_df.head()
