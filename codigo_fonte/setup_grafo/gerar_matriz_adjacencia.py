# ----------------------------------------------------------------------
# PASSO 3: GERAR MATRIZ DE ADJACÊNCIA FINAL
#
# Este é o último script da etapa "setup_grafo". Ele converte a
# lista de arestas ponderadas (u, v, peso) em uma matriz de
# adjacência quadrada e simétrica.
#
# Este formato (matriz) é a entrada final exigida pelo script
# principal de solução do Problema do Carteiro Chinês (CPP).
#
# Entrada: dados_processados/vertices_reordenados.csv (para IDs)
# Entrada: dados_processados/arestas_calc.csv (para pesos)
# Saída:   dados_processados/matriz_adjacencia.csv
# ----------------------------------------------------------------------


import pandas as pd
import numpy as np
import os

# =============================
# 0. Definição de Caminhos
# =============================
PATH_VERTICES = r"dados_processados/vertices_reordenados.csv"
PATH_ARESTAS = r"dados_processados/arestas_com_peso_final.csv"
PATH_SAIDA = r"dados_processados/matriz_adjacencia.csv"
OUT_DIR = r"dados_processados"

# =============================
# 1. Carregar dados
# =============================
print("1. Lendo dados...")
vertices = pd.read_csv(PATH_VERTICES)
arestas = pd.read_csv(PATH_ARESTAS)

# =============================
# 2. Mapear IDs para Índices
# =============================
print("2. Mapeando IDs...")
ids = vertices['id'].tolist()
n = len(ids)
map_id_ind = {vid: i for i, vid in enumerate(ids)}

# =============================
# 3. Construir Matriz
# =============================
print("3. Construindo matriz...")
mat = np.zeros((n, n), dtype=float)

for _, row in arestas.iterrows():
    try:
        o = int(row['origem'])
        d = int(row['destino'])
        peso = row['peso']

        i = map_id_ind[o]
        j = map_id_ind[d]

        mat[i][j] = peso
        mat[j][i] = peso
    except KeyError as e:
        print(f"Aviso: ID {e} da aresta não encontrado na lista de vértices. Pulando aresta.")
    except Exception as e:
        print(f"Erro processando linha {row}: {e}")

# =============================
# 4. Salvar Matriz
# =============================
print("4. Salvando matriz...")
os.makedirs(OUT_DIR, exist_ok=True)

df_mat = pd.DataFrame(mat, index=ids, columns=ids)
df_mat.to_csv(PATH_SAIDA)

print(f"[OK] Matriz de adjacencia gerada com sucesso: {PATH_SAIDA}")