"""
Gera animacao da rota para um agente especifico

Uso:
    python visualizar_animacao_agente.py <agente_id> <dir_tour> <output_file>
"""

import sys
import os
os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import contextily as ctx
import numpy as np
from moviepy import VideoClip

def mplfig_to_npimage(fig):
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    argb = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    argb = argb.reshape((h, w, 4))
    rgba = argb[:, :, [1, 2, 3, 0]]
    rgb = rgba[:, :, :3]
    return rgb

def gerar_animacao_agente(agente_id: int, dir_tour: str, output_file: str):
    """Gera animacao para um agente especifico"""
    
    PATH_VERTICES = "dados_processados/vertices_reordenados.csv"
    tour_file = os.path.join(dir_tour, "tour.csv")
    
    # Configuracoes
    FPS = 30
    
    print(f"Carregando dados do agente {agente_id}...")
    
    # Carregar dados
    vdf = pd.read_csv(PATH_VERTICES)
    
    if not os.path.exists(tour_file):
        print(f"Erro: {tour_file} nao encontrado")
        return False
    
    tdf = pd.read_csv(tour_file)
    
    coord = {
        int(r["id"]): (r["lon"], r["lat"])
        for _, r in vdf.iterrows()
    }
    
    tour = tdf["vertex"].tolist()
    
    # Preparar segmentos
    print("Processando segmentos da rota...")
    segmentos = []
    for i in range(len(tour) - 1):
        u = int(tour[i])
        v = int(tour[i + 1])
        if u in coord and v in coord and coord[u] != coord[v]:
            segmentos.append(LineString([coord[u], coord[v]]))
    
    if not segmentos:
        print("Erro: Nenhum segmento valido encontrado")
        return False
    
    gdf_seg = gpd.GeoDataFrame(geometry=segmentos, crs="EPSG:4326")
    gdf_seg_web = gdf_seg.to_crs(epsg=3857)
    
    xmin, ymin, xmax, ymax = gdf_seg_web.total_bounds
    N = len(gdf_seg_web)
    DUR = N / FPS
    
    print(f"Total de frames: {N}")
    print(f"Duracao do video: {DUR:.2f}s")
    
    # Cores por agente
    cores = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
    cor = cores[agente_id % len(cores)]
    
    # Configurar figura
    print("Configurando a figura base...")
    fig, ax = plt.subplots(figsize=(10, 12))
    
    ctx.add_basemap(ax, crs="EPSG:3857", source=ctx.providers.CartoDB.DarkMatter, zoom=15)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")
    
    (line,) = ax.plot([], [], color=cor, linewidth=3, alpha=0.8)
    (point,) = ax.plot([], [], "o", color="#FFFF00", markersize=10)
    
    # Adicionar titulo
    ax.text(0.5, 0.98, f"Agente {agente_id}", 
            transform=ax.transAxes,
            fontsize=16, 
            color='white',
            ha='center',
            va='top',
            bbox=dict(boxstyle='round', facecolor=cor, alpha=0.8))
    
    plt.tight_layout()
    
    # Funcao de animacao
    def make_frame(t):
        i = int(t * FPS)
        if i >= N:
            i = N - 1
        
        current_segments = gdf_seg_web.iloc[:i+1]
        
        xs = []
        ys = []
        for geom in current_segments.geometry:
            x, y = geom.xy
            xs.extend(list(x))
            ys.extend(list(y))
        
        line.set_data(xs, ys)
        
        geom_last = gdf_seg_web.iloc[i].geometry
        x2, y2 = geom_last.xy
        point.set_data([x2[-1]], [y2[-1]])
        
        return mplfig_to_npimage(fig)
    
    # Criar video
    print(f"Gerando video ({FPS} FPS)... (Isso pode demorar!)")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    clip = VideoClip(make_frame, duration=DUR)
    clip.write_videofile(output_file, fps=FPS, codec="libx264")
    plt.close(fig)
    
    print(f"[OK] Video salvo: {output_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python visualizar_animacao_agente.py <agente_id> <dir_tour> <output_file>")
        sys.exit(1)
    
    agente_id = int(sys.argv[1])
    dir_tour = sys.argv[2]
    output_file = sys.argv[3]
    
    gerar_animacao_agente(agente_id, dir_tour, output_file)
