"""
ALGORITMO: SOLUÇÃO DO PROBLEMA DO CARTEIRO CHINÊS (CPP)

Este é o script principal do projeto. Ele implementa o algoritmo
de Edmonds-Johnson ("Chinese Postman Problem") em Python puro.

O script é otimizado:
1. Usa Dijkstra *apenas* a partir dos nós ímpares.
2. Implementa um 'min_weight_perfect_matching' híbrido (DP exato
   para grafos pequenos, heurística para grafos maiores).
3. Calcula o custo total de forma otimizada (Custo(G) + Custo(Matching)).
4. Usa o algoritmo de Hierholzer para extrair o circuito.

Entrada: (via argumento) dados_processados/matriz_adjacencia.csv
Saídas:  4_resultados_finais/relatorio_tour/
         ├─ tour.csv
         ├─ tour_cost.txt
         ├─ tour_detalhado.csv
         └─ matching_paths.csv
"""

import csv
import heapq
import json
import math
import sys
import os # Necessário para os caminhos de saída
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

# ---------------------------------
# 1. LEITURA DO GRAFO
# ---------------------------------
def read_adjacency_csv(path: str) -> Tuple[Dict[int, Dict[int, float]], List[int]]:
    """
    Função de leitura. Constrói o grafo como um dicionário de dicionários!
    Lê uma matriz de adjacência CSV com index_col=0. Valores 0.0 ou vazios = sem aresta.
    Saída: Retorna (G, nodes) onde G[u][v]=peso e lista ordenada de nós.
    """
    G = {}
    nodes = []
    print(f"Lendo {path}...")
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return {}, []

    header = rows[0][1:]
    nodes = [int(x) for x in header]

    for n in nodes:
        G[n] = {}

    for r in rows[1:]:
        i = int(r[0])
        for j, cell in enumerate(r[1:]):
            col_node = nodes[j]
            if cell is None or cell == "":
                continue
            try:
                w = float(cell)
            except Exception:
                continue
            if math.isfinite(w) and w != 0.0:
                prev = G[i].get(col_node)
                if prev is None or w < prev:
                    G[i][col_node] = w
                    G[col_node][i] = w
    print(f"Grafo lido: {len(nodes)} nós.")
    return G, nodes

# ---------------------------------
# 2. ALGORITMOS DE GRAFO
# ---------------------------------
def dijkstra(graph: Dict[int, Dict[int, float]], source: int) -> Tuple[Dict[int, float], Dict[int, List[int]]]:
    """
    Implementação clássica do algoritmo de Dijkstra usando uma fila de prioridade (heapq).
    Saídas: Retorna (dist, paths) onde dist[v]=distância, paths[v]=caminho do source até v (lista de nós).
    """
    dist = {source: 0.0}
    prev = {}
    pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float('inf')):
            continue
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    paths = {}
    for v in dist:
        cur = v
        path = [cur]
        if cur == source:
            paths[v] = path
            continue
        
        # Reconstrói o caminho
        while cur in prev:
             cur = prev[cur]
             path.append(cur)
             if cur == source:
                 break
        path.reverse()
        paths[v] = path
    return dist, paths

def min_weight_perfect_matching(nodes: List[int], weight_func) -> List[Tuple[int,int]]:
    """
    Min-weight perfect matching (Blossom-like): Pega a lista de nós ímpares (nodes)
    e encontra a forma mais barata de agrupá-los em pares.
    """
    m = len(nodes)
    assert m % 2 == 0, "Para que haja correspondência perfeita, o número de nós deve ser par."

    idx_of = {nodes[i]: i for i in range(m)}
    inv = {i: nodes[i] for i in range(m)}

    C = [[0.0]*m for _ in range(m)]
    for i in range(m):
        for j in range(i+1, m):
            w = weight_func(inv[i], inv[j])
            C[i][j] = w
            C[j][i] = w

    # CASO 1 — DP EXATO (m <= 20)
    if m <= 20:
        FULL = (1 << m) - 1
        memo = {}
        pair_choice = {}

        def dp(mask):
            if mask == 0:
                return 0.0
            if mask in memo:
                return memo[mask]

            i = (mask & -mask).bit_length() - 1
            mask2 = mask ^ (1 << i)
            best = float('inf')
            bestj = -1
            mm = mask2
            while mm:
                jbit = (mm & -mm)
                j = jbit.bit_length() - 1
                val = C[i][j] + dp(mask2 ^ (1 << j))
                if val < best:
                    best = val
                    bestj = j
                mm ^= jbit
            memo[mask] = best
            pair_choice[mask] = (i, bestj)
            return best

        dp(FULL)
        mask = FULL
        pairs = []
        while mask:
            i, j = pair_choice[mask]
            pairs.append((inv[i], inv[j]))
            mask ^= (1 << i)
            mask ^= (1 << j)
        return pairs

    # CASO 2 — HEURÍSTICA GREEDY + LOCAL IMPROVEMENT (m > 20)
    pairs = []
    used = [False]*m
    all_pairs = [(C[i][j], i, j) for i in range(m) for j in range(i+1, m)]
    all_pairs.sort()
    for w,i,j in all_pairs:
        if not used[i] and not used[j]:
            used[i] = used[j] = True
            pairs.append((i,j))
    matching = pairs

    improved = True
    iters = 0
    while improved and iters < 1000:
        improved = False
        iters += 1
        nmatch = len(matching)
        for p in range(nmatch):
            a,b = matching[p]
            for q in range(p+1, nmatch):
                c,d = matching[q]
                cur = C[a][b] + C[c][d]
                new1 = C[a][c] + C[b][d]
                new2 = C[a][d] + C[b][c]
                if new1 + 1e-12 < cur:
                    matching[p] = (a,c)
                    matching[q] = (b,d)
                    improved = True
                    break
                elif new2 + 1e-12 < cur:
                    matching[p] = (a,d)
                    matching[q] = (b,c)
                    improved = True
                    break
            if improved:
                break
    result = []
    for i,j in matching:
        result.append((inv[i], inv[j]))
    return result

def build_multigraph_with_counts(graph: Dict[int, Dict[int, float]], matching_pairs: List[Tuple[int,int]], paths_between: Dict[Tuple[int,int], List[int]]):
    """
    MG[u][v] armazena a multiplicidade (contagem) de arestas entre u e v.
    """
    MG = defaultdict(Counter)
    for u in graph:
        for v, w in graph[u].items():
            if u < v:
                MG[u][v] += 1
                MG[v][u] += 1
    for u,v in matching_pairs:
        path = paths_between[(u,v)]
        for a,b in zip(path[:-1], path[1:]):
            MG[a][b] += 1
            MG[b][a] += 1
    return MG

def hierholzer_multigraph(MG: Dict[int, Counter], start=None) -> List[Tuple[int,int]]:
    """
    Implementação clássica do algoritmo de Hierholzer usando uma pilha (stack).
    """
    if start is None:
        start = None
        for u, cnts in MG.items():
            deg = sum(cnts.values())
            if deg > 0:
                start = u
                break
    if start is None:
        return []

    mg = {u: Counter(cnts) for u,cnts in MG.items()}
    circuit = []
    stack = [start]
    while stack:
        v = stack[-1]
        if mg.get(v):
            u = next(iter(mg[v])) # Pega um vizinho
            
            # Remove a aresta (v, u)
            mg[v][u] -= 1
            if mg[v][u] == 0:
                del mg[v][u]
            mg[u][v] -= 1
            if mg[u][v] == 0:
                del mg[u][v]
            
            stack.append(u)
        else:
            stack.pop()
            if stack:
                circuit.append((stack[-1], v))
    return circuit

# ---------------------------------
# 3. FLUXO PRINCIPAL (PIPELINE)
# ---------------------------------
def solve_cpp_puro(G: Dict[int, Dict[int, float]], nodes: List[int], out_dir: str):
    """
    Fluxo Principal (Pipeline) que executa a solução do CPP.
    """
    if not G:
        print("Grafo vazio.")
        return

    print("3.1. Analisando graus e conectividade...")
    degrees = {u: len(G[u]) for u in G}
    odd_nodes = [u for u,d in degrees.items() if d % 2 == 1]
    non_isolated = [u for u in G if degrees[u] > 0]

    # Checagem de conectividade
    if non_isolated:
        start = non_isolated[0]
        visited = set()
        q = [start]
        while q:
            x = q.pop()
            if x in visited: continue
            visited.add(x)
            for y in G[x]:
                if y not in visited:
                    q.append(y)
        if set(non_isolated) - visited:
            raise ValueError("Grafo não é conexo entre vértices com arestas.")
    print(f"   -> Encontrados {len(odd_nodes)} nos de grau impar.")

    # Caso 1: Grafo já é Euleriano
    if not odd_nodes:
        print("3.2. Grafo já é Euleriano. Extraindo circuito...")
        MG_counts = defaultdict(Counter)
        for u in G:
            for v in G[u]:
                if u < v:
                    MG_counts[u][v] += 1
                    MG_counts[v][u] += 1
        euler_edges = hierholzer_multigraph(MG_counts)
        tour_vertices = []
        if euler_edges:
            tour_vertices = [euler_edges[0][0]] + [v for (_, v) in euler_edges]
        cost_original = sum(w for u in G for v,w in G[u].items() if u < v)
        
        print("3.3. Salvando resultados...")
        save_outputs(out_dir, tour_vertices, euler_edges, cost_original, MG_counts, {}, {})
        return

    # Caso 2: Grafo não-Euleriano (precisa de emparelhamento)
    print("3.2. Calculando caminhos mínimos (Dijkstra) a partir de nós ímpares...")
    length = {}
    paths = {}
    for i, u in enumerate(odd_nodes):
        print(f"   -> Processando no impar {i+1}/{len(odd_nodes)} (ID: {u})")
        dist, p = dijkstra(G, u)
        length[u] = dist
        paths[u] = p

    def dist_uv(a,b):
        return length[a][b]

    print("3.3. Calculando emparelhamento perfeito de custo mínimo...")
    if len(odd_nodes) % 2 != 0:
        raise ValueError("Contagem de nós ímpares não é par. Isso não deveria acontecer.")
    matching_pairs = min_weight_perfect_matching(odd_nodes, dist_uv)
    print("   -> Emparelhamento concluido.")

    paths_between = {}
    for u,v in matching_pairs:
        if v in paths[u]:
            p = paths[u][v]
        else:
            p = list(reversed(paths[v][u]))
        paths_between[(u,v)] = p
        paths_between[(v,u)] = list(reversed(p))

    print("3.4. Construindo multigrafo aumentado...")
    MG_counts = build_multigraph_with_counts(G, matching_pairs, paths_between)

    print("3.5. Extraindo circuito Euleriano (Hierholzer)...")
    euler_edges = hierholzer_multigraph(MG_counts)
    tour_vertices = []
    if euler_edges:
        tour_vertices = [euler_edges[0][0]] + [v for (_, v) in euler_edges]

    print("3.6. Calculando custo total (otimizado)...")
    cost_original = sum(w for u in G for v,w in G[u].items() if u < v)
    cost_matching = sum(dist_uv(u,v) for u,v in matching_pairs)
    total_cost = cost_original + cost_matching

    print("3.7. Salvando resultados...")
    save_outputs(out_dir, tour_vertices, euler_edges, total_cost, MG_counts, matching_pairs, paths_between)

# ---------------------------------
# 4. SALVAR SAÍDAS
# ---------------------------------

# Variável global para 'save_outputs' acessar os pesos do grafo lido no 'main'
GLOBAL_G = {}

def save_outputs(out_dir: str, tour_vertices, euler_edges, total_cost, MG_counts, matching_pairs, paths_between):
    """
    Função de utilidade para gravar os 4 arquivos de saída na pasta 'out_dir'.
    """
    # Garante que o diretório de saída exista
    os.makedirs(out_dir, exist_ok=True)
    
    # Define os caminhos completos
    path_tour = os.path.join(out_dir, "tour.csv")
    path_cost = os.path.join(out_dir, "tour_cost.txt")
    path_detailed = os.path.join(out_dir, "tour_detalhado.csv")
    path_matching = os.path.join(out_dir, "matching_paths.csv")

    if tour_vertices:
        with open(path_tour, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["order","vertex"])
            for i,v in enumerate(tour_vertices):
                wr.writerow([i, v])

    with open(path_cost, "w", encoding="utf-8") as f:
        f.write(str(total_cost))

    if euler_edges:
        cum = 0.0
        with open(path_detailed, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["order","u","v","weight","cumulative_cost"])
            for i,(u,v) in enumerate(euler_edges):
                w = 1.0
                try:
                    # Usa GLOBAL_G para pegar o peso original da aresta
                    w = GLOBAL_G[u][v]
                except Exception:
                    # Fallback caso a aresta (u,v) não exista (improvável)
                    try:
                        w = GLOBAL_G[v][u]
                    except Exception:
                        pass # Mantém w=1.0
                cum += w
                wr.writerow([i, u, v, w, cum])

    if matching_pairs:
        with open(path_matching, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["u","v","path_vertices","path_edges"])
            for pair in (matching_pairs if isinstance(matching_pairs, list) else list(matching_pairs)):
                u, v = pair[0], pair[1]
                p = paths_between.get((u,v)) or []
                edges = ";".join(f"{a}-{b}" for a,b in zip(p[:-1], p[1:]))
                wr.writerow([u, v, json.dumps(p, ensure_ascii=False), edges])

    print(f"Resultados salvos em: {out_dir}")
    print(f"Custo total final: {total_cost}")

# ---------------------------------
# 5. EXECUÇÃO
# ---------------------------------
def main():
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho para a matriz de adjacência.")
        print("Uso: python resolver_cpp.py dados_processados/matriz_adjacencia.csv")
        sys.exit(1)
    
    path = sys.argv[1]
    
    # Define o diretório de saída
    OUT_DIR = r"resultados_finais/relatorio_tour" 
    
    # Lê o grafo UMA VEZ e o armazena na variável global
    # para que 'save_outputs' possa consultar os pesos
    print("1. Lendo o grafo...")
    G, nodes = read_adjacency_csv(path)
    global GLOBAL_G
    GLOBAL_G = G
    
    print("\n2. Iniciando a solução do CPP...")
    # Passa G, nodes e OUT_DIR para a função principal
    solve_cpp_puro(G, nodes, OUT_DIR)
    
    print("\n[OK] Processo concluido com sucesso.")

if __name__ == "__main__":
    main()