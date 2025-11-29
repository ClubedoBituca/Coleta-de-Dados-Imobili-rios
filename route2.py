import pandas as pd
import os
import heapq
import numpy as np

# ================= CONFIGURAÇÕES =================
ARQUIVO_MATRIZ = os.path.join('dados_processados', 'matriz_adjacencia.csv')
ARQUIVO_TOUR_DETALHADO = os.path.join('resultados_finais', 'relatorio_tour', 'tour_detalhado.csv')
PASTA_SAIDA = os.path.join('dados_processados', 'clusters_finais')
NUM_AGENTES = 3
DEPOT_NODE = 0  # Vértice da base (Depósito)

def carregar_dados_iniciais(caminho_matriz):
    """
    Carrega a matriz para obter os labels (índices originais) e cria o grafo 
    para o algoritmo de Dijkstra.
    Retorna: (Grafo Dict, Lista de Labels)
    """
    if not os.path.exists(caminho_matriz):
        raise FileNotFoundError(f"Matriz não encontrada: {caminho_matriz}")
        
    # Lê o DataFrame completo para preservar a estrutura (index/columns)
    df = pd.read_csv(caminho_matriz, index_col=0)
    
    # Tratamento de Tipos para garantir consistência (Int preferencialmente)
    try:
        df.index = df.index.astype(int)
        df.columns = df.columns.astype(int)
        labels = df.index.tolist()
    except ValueError:
        print("Aviso: Usando labels como string.")
        labels = df.index.astype(str).tolist()

    # Constrói o Grafo (Dicionário de Adjacência) para performance
    print("Construindo grafo em memória...")
    grafo = {}
    
    # O método stack() transforma a matriz em uma Série: (linha, coluna) -> valor
    # Isso é muito mais rápido que iterar
    matriz_empilhada = df.stack()
    
    for (u, v), peso in matriz_empilhada.items():
        if u == v: continue # Pula auto-loops
        if peso <= 0: continue # Pula arestas inválidas para roteamento
        
        # Garante tipo nativo do Python (não numpy)
        u_val, v_val = (int(u), int(v)) if isinstance(u, (int, np.integer)) else (u, v)
        w_val = float(peso)
        
        if u_val not in grafo: grafo[u_val] = {}
        if v_val not in grafo: grafo[v_val] = {}
        
        grafo[u_val][v_val] = w_val

    print(f"Grafo carregado: {len(grafo)} vértices conectados.")
    return grafo, labels

def carregar_tour(caminho_tour):
    """Lê o arquivo tour_detalhado.csv gerado pelo seu CPP."""
    if not os.path.exists(caminho_tour):
        raise FileNotFoundError(f"Arquivo {caminho_tour} não encontrado.")
        
    df = pd.read_csv(caminho_tour)
    df.columns = df.columns.str.strip()
    
    # Mapeia colunas caso os nomes variem
    cols_map = {}
    if 'u' not in df.columns: cols_map[df.columns[1]] = 'u'
    if 'v' not in df.columns: cols_map[df.columns[2]] = 'v'
    if 'weight' not in df.columns: cols_map[df.columns[3]] = 'weight'
    if cols_map:
        df.rename(columns=cols_map, inplace=True)
    
    # Garante int
    df['u'] = df['u'].astype(int)
    df['v'] = df['v'].astype(int)
    return df

def dijkstra_puro(grafo, origem, destino):
    """
    Calcula o menor caminho entre origem e destino.
    Retorna lista de arestas: [{'u':..., 'v':..., 'weight':...}, ...]
    """
    if origem == destino:
        return [], 0.0
    
    if origem not in grafo or destino not in grafo:
        # Fallback silencioso se for nó isolado
        return [], 0.0

    fila = [(0.0, origem)]
    distancias = {origem: 0.0}
    anteriores = {origem: None}
    
    encontrou = False
    custo_final = 0.0

    while fila:
        d_atual, u = heapq.heappop(fila)
        
        if u == destino:
            custo_final = d_atual
            encontrou = True
            break
        
        if d_atual > distancias.get(u, float('inf')):
            continue
        
        for v, peso in grafo.get(u, {}).items():
            nova_dist = d_atual + peso
            if nova_dist < distancias.get(v, float('inf')):
                distancias[v] = nova_dist
                anteriores[v] = u
                heapq.heappush(fila, (nova_dist, v))
    
    if not encontrou:
        print(f"  [Aviso] Sem caminho entre {origem} e {destino}.")
        return [], 0.0
    
    # Reconstrução (Backtracking)
    caminho = []
    curr = destino
    while curr != origem:
        prev = anteriores[curr]
        w = grafo[prev][curr]
        caminho.append({'u': prev, 'v': curr, 'weight': w, 'tipo': 'deslocamento'})
        curr = prev
    
    caminho.reverse()
    return caminho, custo_final

def dividir_tour_e_gerar_matrizes(df_tour, grafo, labels, n_agentes):
    print("\n=== Dividindo Tour e Gerando Matrizes de Cluster ===")
    
    custo_total = df_tour['weight'].sum()
    meta = custo_total / n_agentes
    print(f"Meta por agente: ~{meta:.2f}")
    
    agente_id = 0
    custo_atual = 0.0
    
    # Lista para acumular as arestas do agente atual
    # Cada item é dict: {'u': u, 'v': v, 'weight': w}
    arestas_cluster = []
    
    total_linhas = len(df_tour)
    
    for idx, row in df_tour.iterrows():
        u, v = int(row['u']), int(row['v'])
        w = float(row['weight'])
        
        # 1. Conexão Inicial (Ida da Base)
        if len(arestas_cluster) == 0:
            if u != DEPOT_NODE:
                caminho_ida, _ = dijkstra_puro(grafo, DEPOT_NODE, u)
                arestas_cluster.extend(caminho_ida)
        
        # 2. Aresta de Serviço (do Tour)
        arestas_cluster.append({'u': u, 'v': v, 'weight': w, 'tipo': 'servico'})
        custo_atual += w
        
        # 3. Critério de Corte
        pode_cortar = (custo_atual >= meta) and (agente_id < n_agentes - 1) and (idx < total_linhas - 1)
        
        if pode_cortar:
            print(f"Agente {agente_id} finalizado em {v} (Carga: {custo_atual:.2f})")
            
            # Conexão Final (Volta para Base)
            if v != DEPOT_NODE:
                caminho_volta, _ = dijkstra_puro(grafo, v, DEPOT_NODE)
                arestas_cluster.extend(caminho_volta)
            
            # EXPORTAR IMEDIATAMENTE
            salvar_matriz_cluster(agente_id, arestas_cluster, labels)
            
            # Reseta para próximo agente
            agente_id += 1
            custo_atual = 0.0
            arestas_cluster = []
            
    # 4. Finaliza Último Agente
    if arestas_cluster:
        ultimo_v = int(df_tour.iloc[-1]['v'])
        print(f"Agente {agente_id} finalizado em {ultimo_v} (Restante)")
        
        if ultimo_v != DEPOT_NODE:
            caminho_volta, _ = dijkstra_puro(grafo, ultimo_v, DEPOT_NODE)
            arestas_cluster.extend(caminho_volta)
            
        salvar_matriz_cluster(agente_id, arestas_cluster, labels)

def salvar_matriz_cluster(agente_id, lista_arestas, labels):
    """
    Cria uma matriz N x N zerada e preenche apenas as arestas presentes na lista.
    Salva como CSV compatível com o formato original.
    """
    if not os.path.exists(PASTA_SAIDA):
        os.makedirs(PASTA_SAIDA)
        
    # Cria DataFrame Vazio (Template)
    # Usa 0.0 para indicar ausência de aresta (ou conforme seu padrão CPP)
    df_matriz = pd.DataFrame(0.0, index=labels, columns=labels)
    
    count_servico = 0
    count_desloc = 0
    
    for aresta in lista_arestas:
        u, v = aresta['u'], aresta['v']
        w = aresta['weight']
        
        # Verifica se os índices existem (segurança)
        if u in df_matriz.index and v in df_matriz.columns:
            # Preenche simetricamente
            df_matriz.at[u, v] = w
            df_matriz.at[v, u] = w
            
            if aresta.get('tipo') == 'servico':
                count_servico += 1
            else:
                count_desloc += 1
                
    nome_arquivo = f"matriz_agente_{agente_id}.csv"
    caminho = os.path.join(PASTA_SAIDA, nome_arquivo)
    df_matriz.to_csv(caminho)
    
    print(f"  -> Exportado: {nome_arquivo}")
    print(f"     (Arestas Serviço: {count_servico} | Arestas Conexão/Dijkstra: {count_desloc})")

def main():
    try:
        # Carrega grafo e labels
        grafo, labels = carregar_dados_iniciais(ARQUIVO_MATRIZ)
        
        # Carrega tour
        df_tour = carregar_tour(ARQUIVO_TOUR_DETALHADO)
        
        # Processa e Salva
        dividir_tour_e_gerar_matrizes(df_tour, grafo, labels, NUM_AGENTES)
        
        print("\nConcluído. As matrizes geradas contêm os subgrafos conectados prontos para o CPP.")
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()