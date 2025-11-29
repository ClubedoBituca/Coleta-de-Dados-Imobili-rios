"""
Gera mapa interativo para um agente específico

Uso:
    python visualizar_mapa_agente.py <agente_id> <dir_tour> <output_file>
"""

import sys
import os
import pandas as pd
import folium
from folium.plugins import BeautifyIcon
from datetime import datetime

def gerar_mapa_agente(agente_id: int, dir_tour: str, output_file: str):
    """Gera mapa interativo para um agente específico"""
    
    # Caminhos
    PATH_VERTICES = "dados_processados/vertices_reordenados.csv"
    tour_file = os.path.join(dir_tour, "tour.csv")
    
    # Verificar se arquivos existem
    if not os.path.exists(PATH_VERTICES):
        print(f"Erro: {PATH_VERTICES} não encontrado")
        return False
    
    if not os.path.exists(tour_file):
        print(f"Erro: {tour_file} não encontrado")
        return False
    
    # Carregar dados
    print(f"Carregando dados do agente {agente_id}...")
    vdf = pd.read_csv(PATH_VERTICES)
    tdf = pd.read_csv(tour_file)
    
    # Criar dicionário de coordenadas
    coord = {
        int(r["id"]): (r["lat"], r["lon"])
        for _, r in vdf.iterrows()
    }
    
    tour = tdf["vertex"].tolist()
    if not tour:
        print("Erro: Tour vazio")
        return False
    
    # Criar mapa
    lat0, lon0 = coord[tour[0]]
    m = folium.Map(location=[lat0, lon0], zoom_start=16, tiles=None)
    
    # Adicionar rota
    polyline_coords = []
    for v in tour:
        if v in coord:
            polyline_coords.append(coord[v])
    
    # Cores diferentes para cada agente
    cores = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
    cor = cores[agente_id % len(cores)]
    
    folium.PolyLine(
        locations=polyline_coords,
        weight=4,
        color=cor,
        tooltip=f"Rota Agente {agente_id}"
    ).add_to(m)
    
    # Adicionar marcadores
    for v in tour:
        if v in coord:
            lat, lon = coord[v]
            icon = BeautifyIcon(
                icon_shape="marker",
                border_color="#ffffff",
                border_width=1,
                text_color="#ffffff",
                background_color=cor,
                number=str(v),
                inner_icon_style="font-size:12px;"
            )
            folium.Marker(location=[lat, lon], icon=icon, draggable=False).add_to(m)
    
    # Adicionar camada de satélite
    esri_imagery_url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    )
    folium.TileLayer(
        tiles=esri_imagery_url,
        attr="Tiles © Esri",
        name="Esri WorldImagery",
        overlay=False,
        control=True,
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    # Salvar
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    m.save(output_file)
    
    print(f"[OK] Mapa salvo: {output_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python visualizar_mapa_agente.py <agente_id> <dir_tour> <output_file>")
        sys.exit(1)
    
    agente_id = int(sys.argv[1])
    dir_tour = sys.argv[2]
    output_file = sys.argv[3]
    
    gerar_mapa_agente(agente_id, dir_tour, output_file)
