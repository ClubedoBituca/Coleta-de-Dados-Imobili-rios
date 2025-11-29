# ---------------------------------------------------------
# VISUALIZAÇÃO DO GRAFO COMPLETO SOBRE MAPA DE RUA (FOLIUM)
# ---------------------------------------------------------

import pandas as pd
import folium
from folium.plugins import BeautifyIcon
import os

# ================================
# 0. Caminhos dos arquivos
# ================================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

PATH_VERTICES = os.path.join(ROOT, "dados_processados", "vertices_reordenados.csv")
PATH_ADJ      = os.path.join(ROOT, "dados_processados", "matriz_adjacencia.csv")
PATH_SAIDA    = os.path.join(ROOT, "resultados_finais", "mapa_grafo_completo.html")

# ================================
# 1. Ler CSV de vértices
# ================================
print("1. Lendo coordenadas dos vértices...")
vdf = pd.read_csv(PATH_VERTICES)

# Criar dicionário: id → (lat, lon)
coord = {
    int(r["id"]): (r["lat"], r["lon"])
    for _, r in vdf.iterrows()
}

# ================================
# 2. Ler matriz de adjacência
# ================================
print("2. Lendo matriz de adjacência...")
adj = pd.read_csv(PATH_ADJ, index_col=0)

# Garantir que tudo seja numérico
adj.columns = adj.columns.astype(int)
adj.index = adj.index.astype(int)

# ================================
# 3. Criar mapa Folium
# ================================
print("3. Criando mapa...")

# Pega um vértice qualquer como centro
first = vdf.iloc[0]
lat0, lon0 = first["lat"], first["lon"]

m = folium.Map(location=[lat0, lon0], zoom_start=16)

# === ADICIONAR TILE ESRI (como solicitado) ===
esri_imagery_url = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)

folium.TileLayer(
    tiles=esri_imagery_url,
    attr="Tiles © Esri",
    name="Esri WorldImagery",
    overlay=False,
    control=True,
).add_to(m)

# ================================
# 4. Plottar todas as arestas do grafo
# ================================
print("4. Plotando arestas...")

for i in adj.index:
    for j in adj.columns:
        if adj.at[i, j] != 0:  # existe aresta
            if i in coord and j in coord:
                folium.PolyLine(
                    locations=[coord[i], coord[j]],
                    color="#00A3FF",
                    weight=2,
                    opacity=0.8
                ).add_to(m)

# ================================
# 5. Plottar vértices
# ================================
print("5. Plotando vértices...")

for vid, (lat, lon) in coord.items():
    folium.Marker(
        location=[lat, lon],
        popup=f"Vértice {vid}",
        icon=BeautifyIcon(
            number=str(vid),       # <<< número exibido no marcador
            border_color="#FF0000",
            text_color="white",
            background_color="#FF0000",
            border_width=1
        )
    ).add_to(m)

# ================================
# 6. Finalizar
# ================================
folium.LayerControl().add_to(m)

os.makedirs(os.path.dirname(PATH_SAIDA), exist_ok=True)
m.save(PATH_SAIDA)

print(f"\nMapa salvo em: {PATH_SAIDA}\n")
print("Visualização completa do grafo gerada com sucesso!")
