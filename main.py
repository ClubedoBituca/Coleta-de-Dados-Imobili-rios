"""
PIPELINE COMPLETO DE OTIMIZAÇÃO DE ROTAS PARA COLETA DE DADOS IMOBILIÁRIOS

Este script orquestra todo o processo chamando os scripts existentes na ordem correta.

Uso:
    python main_pipeline_v2.py <num_agentes>
    
Exemplo:
    python main_pipeline_v2.py 2
"""

import sys
import os
import time
import subprocess
import shutil
from datetime import datetime

# ============= CONFIGURAÇÕES =============
CUSTO_HORA_AGENTE = 50.0
HORAS_TRABALHO_DIA = 8

# ============= FUNÇÕES AUXILIARES =============

def obter_proximo_numero_grafo():
    """Retorna o próximo número sequencial para a pasta de resultados"""
    base_dir = "resultados"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        return 1
    
    # Listar todas as pastas grafo-X
    pastas = [d for d in os.listdir(base_dir) if d.startswith("grafo-")]
    
    if not pastas:
        return 1
    
    # Extrair números
    numeros = []
    for pasta in pastas:
        try:
            num = int(pasta.split("-")[1])
            numeros.append(num)
        except:
            continue
    
    if not numeros:
        return 1
    
    return max(numeros) + 1

def print_header(texto: str):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {texto}")
    print("=" * 80)

def print_step(numero: int, texto: str):
    """Imprime um passo do pipeline"""
    print(f"\n[PASSO {numero}] {texto}")
    print("-" * 80)

def executar_script(comando: list, descricao: str) -> bool:
    """Executa um script Python e retorna True se bem-sucedido"""
    print(f"  -> Executando: {descricao}")
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if resultado.stdout:
            print(resultado.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [X] ERRO ao executar {descricao}")
        print(f"      Codigo de saida: {e.returncode}")
        if e.stderr:
            print(f"      Erro: {e.stderr}")
        return False

def ler_custo_tour(caminho: str) -> float:
    """Lê o custo de um tour"""
    try:
        with open(caminho, 'r') as f:
            return float(f.read().strip())
    except:
        return 0.0

def calcular_metricas(custos_agentes: list, num_agentes: int):
    """Calcula e exibe métricas finais"""
    print_header("METRICAS FINAIS E ANALISE DE CUSTOS")
    
    custos_min = [c / 60 for c in custos_agentes]
    custos_horas = [c / 3600 for c in custos_agentes]
    
    tempo_total_seq = sum(custos_agentes)
    tempo_total_seq_min = tempo_total_seq / 60
    tempo_total_seq_horas = tempo_total_seq / 3600
    
    tempo_total_par = max(custos_agentes) if custos_agentes else 0
    tempo_total_par_min = tempo_total_par / 60
    tempo_total_par_horas = tempo_total_par / 3600
    
    dias_seq = tempo_total_seq_horas / HORAS_TRABALHO_DIA
    dias_par = tempo_total_par_horas / HORAS_TRABALHO_DIA
    
    custo_total_seq = tempo_total_seq_horas * CUSTO_HORA_AGENTE
    custo_total_par = tempo_total_par_horas * CUSTO_HORA_AGENTE * num_agentes
    
    print(f"\n[DADOS] RESUMO POR AGENTE:")
    print("-" * 80)
    for i, (custo_m, custo_h) in enumerate(zip(custos_min, custos_horas)):
        print(f"  Agente {i}:")
        print(f"    * Tempo de trabalho: {custo_m:.2f} min ({custo_h:.2f} horas)")
        print(f"    * Custo operacional: R$ {custo_h * CUSTO_HORA_AGENTE:.2f}")
    
    print(f"\n[TEMPO] TEMPO TOTAL:")
    print("-" * 80)
    print(f"  Sequencial (1 agente fazendo tudo):")
    print(f"    * {tempo_total_seq_min:.2f} minutos")
    print(f"    * {tempo_total_seq_horas:.2f} horas")
    print(f"    * {dias_seq:.2f} dias uteis")
    
    if num_agentes > 1:
        print(f"\n  Paralelo ({num_agentes} agentes simultaneos):")
        print(f"    * {tempo_total_par_min:.2f} minutos")
        print(f"    * {tempo_total_par_horas:.2f} horas")
        print(f"    * {dias_par:.2f} dias uteis")
        
        economia_tempo = ((tempo_total_seq - tempo_total_par) / tempo_total_seq) * 100
        print(f"\n  [DICA] Economia de tempo: {economia_tempo:.1f}%")
    
    print(f"\n[CUSTO] CUSTOS OPERACIONAIS:")
    print("-" * 80)
    print(f"  Custo por hora/agente: R$ {CUSTO_HORA_AGENTE:.2f}")
    print(f"\n  Cenario Sequencial (1 agente):")
    print(f"    * Custo total: R$ {custo_total_seq:.2f}")
    
    if num_agentes > 1:
        print(f"\n  Cenario Paralelo ({num_agentes} agentes):")
        print(f"    * Custo total: R$ {custo_total_par:.2f}")
        
        if custo_total_par > custo_total_seq:
            diferenca = custo_total_par - custo_total_seq
            print(f"    * Custo adicional: R$ {diferenca:.2f} (+{(diferenca/custo_total_seq)*100:.1f}%)")
        else:
            economia = custo_total_seq - custo_total_par
            print(f"    * Economia: R$ {economia:.2f} (-{(economia/custo_total_seq)*100:.1f}%)")
    
    # Salvar relatório
    relatorio_file = f"resultados_finais/relatorio_metricas_{num_agentes}_agentes.txt"
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATORIO DE METRICAS E CUSTOS OPERACIONAIS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Numero de agentes: {num_agentes}\n\n")
        
        f.write("RESUMO POR AGENTE:\n")
        f.write("-" * 80 + "\n")
        for i, (custo_m, custo_h) in enumerate(zip(custos_min, custos_horas)):
            f.write(f"Agente {i}: {custo_m:.2f} min ({custo_h:.2f} h) - R$ {custo_h * CUSTO_HORA_AGENTE:.2f}\n")
        
        f.write(f"\nTEMPO TOTAL:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Sequencial: {tempo_total_seq_horas:.2f} h ({dias_seq:.2f} dias)\n")
        if num_agentes > 1:
            f.write(f"Paralelo: {tempo_total_par_horas:.2f} h ({dias_par:.2f} dias)\n")
            f.write(f"Economia: {economia_tempo:.1f}%\n")
        
        f.write(f"\nCUSTOS OPERACIONAIS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Sequencial: R$ {custo_total_seq:.2f}\n")
        if num_agentes > 1:
            f.write(f"Paralelo: R$ {custo_total_par:.2f}\n")
    
    print(f"\n  [OK] Relatorio salvo: {relatorio_file}")

# ============= PIPELINE PRINCIPAL =============

def main():
    """Função principal que executa todo o pipeline"""
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("=" * 80)
        print("PIPELINE DE OTIMIZACAO DE ROTAS")
        print("=" * 80)
        print()
        print("Quantos agentes voce deseja usar?")
        print("  * 1 agente: Um unico coletor faz todo o trabalho")
        print("  * 2 agentes: Divide o trabalho entre dois coletores")
        print("  * 3+ agentes: Divide entre multiplos coletores")
        print()
        
        try:
            num_agentes_input = input("Digite o numero de agentes (1-10): ").strip()
            num_agentes = int(num_agentes_input)
            if num_agentes < 1 or num_agentes > 10:
                raise ValueError("Numero de agentes deve estar entre 1 e 10")
        except (ValueError, KeyboardInterrupt):
            print()
            print("[ERRO] Entrada invalida ou operacao cancelada")
            print()
            print("[DICA] Voce tambem pode executar diretamente:")
            print("   python main_pipeline_v2.py <num_agentes>")
            print("   Exemplo: python main_pipeline_v2.py 2")
            sys.exit(1)
    else:
        try:
            num_agentes = int(sys.argv[1])
            if num_agentes < 1:
                raise ValueError("Numero de agentes deve ser >= 1")
        except ValueError as e:
            print(f"Erro: {e}")
            print("O numero de agentes deve ser um inteiro positivo")
            sys.exit(1)
    
    # Início
    inicio_total = time.time()
    
    # Obter número sequencial e criar pasta de resultados
    num_grafo = obter_proximo_numero_grafo()
    DIR_RESULTADOS = f"resultados/grafo-{num_grafo}"
    DIR_VISUALIZACOES = os.path.join(DIR_RESULTADOS, "visualizacoes")
    DIR_TOUR = os.path.join(DIR_RESULTADOS, "relatorio_tour")
    
    print_header(f"PIPELINE DE OTIMIZACAO DE ROTAS - {num_agentes} AGENTE(S)")
    print(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Pasta de resultados: {DIR_RESULTADOS}")
    
    # Criar diretórios necessários
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    os.makedirs(DIR_VISUALIZACOES, exist_ok=True)
    os.makedirs(DIR_TOUR, exist_ok=True)
    
    # ===== PASSO 1: Calcular pesos com casas =====
    print_step(1, "Calculando pesos das arestas (distancia + tempo de servico)")
    if not executar_script(
        ["python", "calcular_peso_com_casas.py"],
        "calcular_peso_com_casas.py"
    ):
        print("[X] Falha no calculo de pesos")
        sys.exit(1)
    
    # ===== PASSO 2: Gerar matriz de adjacência =====
    print_step(2, "Gerando matriz de adjacencia")
    if not executar_script(
        ["python", "codigo_fonte/setup_grafo/gerar_matriz_adjacencia.py"],
        "gerar_matriz_adjacencia.py"
    ):
        print("[X] Falha na geracao da matriz")
        sys.exit(1)
    
    # ===== PASSO 3: Visualizar grafo estático =====
    print_step(3, "Gerando visualizacao do grafo estatico")
    executar_script(
        ["python", "codigo_fonte/visualizacao/visualizar_grafo_estatico.py"],
        "visualizar_grafo_estatico.py"
    )
    
    # ===== PASSO 4: Resolver CPP inicial =====
    print_step(4, "Resolvendo Problema do Carteiro Chines (CPP) - Tour completo")
    
    # Temporariamente mover para resultados_finais (o script resolver_cpp.py usa esse caminho fixo)
    # Depois vamos mover para a pasta correta
    if not executar_script(
        ["python", "codigo_fonte/algoritmo_cpp/resolver_cpp.py", "dados_processados/matriz_adjacencia.csv"],
        "resolver_cpp.py"
    ):
        print("[X] Falha na resolucao do CPP")
        sys.exit(1)
    
    # Mover resultados para a pasta correta
    if os.path.exists("resultados_finais/relatorio_tour"):
        import shutil
        for arquivo in os.listdir("resultados_finais/relatorio_tour"):
            origem = os.path.join("resultados_finais/relatorio_tour", arquivo)
            destino = os.path.join(DIR_TOUR, arquivo)
            if os.path.isfile(origem):
                shutil.copy2(origem, destino)
    
    custos_agentes = []
    
    # ===== PASSO 5: Dividir em clusters (se múltiplos agentes) =====
    if num_agentes > 1:
        print_step(5, f"Dividindo tour em {num_agentes} clusters")
        
        # Modificar route2.py temporariamente
        with open("route2.py", 'r', encoding='utf-8') as f:
            conteudo_original = f.read()
        
        conteudo_modificado = conteudo_original.replace(
            "NUM_AGENTES = 3",
            f"NUM_AGENTES = {num_agentes}"
        )
        
        with open("route2_temp.py", 'w', encoding='utf-8') as f:
            f.write(conteudo_modificado)
        
        if not executar_script(
            ["python", "route2_temp.py"],
            "route2.py (divisao em clusters)"
        ):
            print("[X] Falha na divisao em clusters")
            if os.path.exists("route2_temp.py"):
                os.remove("route2_temp.py")
            sys.exit(1)
        
        if os.path.exists("route2_temp.py"):
            os.remove("route2_temp.py")
        
        # ===== PASSO 6: Resolver CPP para cada cluster =====
        print_step(6, f"Resolvendo CPP para cada um dos {num_agentes} agentes")
        
        for i in range(num_agentes):
            matriz_cluster = f"dados_processados/clusters_finais/matriz_agente_{i}.csv"
            
            if not os.path.exists(matriz_cluster):
                print(f"  [X] Matriz do cluster {i} nao encontrada")
                continue
            
            # Criar diretório para este agente
            dir_agente = os.path.join(DIR_RESULTADOS, f"agente_{i}")
            os.makedirs(dir_agente, exist_ok=True)
            
            print(f"\n  -> Resolvendo CPP para agente {i}...")
            
            # Executar resolver_cpp.py
            if executar_script(
                ["python", "codigo_fonte/algoritmo_cpp/resolver_cpp.py", matriz_cluster],
                f"resolver_cpp.py (agente {i})"
            ):
                # Mover arquivos para o diretório do agente
                arquivos_tour = ["tour.csv", "tour_cost.txt", "tour_detalhado.csv", "matching_paths.csv"]
                for arquivo in arquivos_tour:
                    origem = f"resultados_finais/relatorio_tour/{arquivo}"
                    destino = f"{dir_agente}/{arquivo}"
                    if os.path.exists(origem):
                        shutil.move(origem, destino)
                
                # Ler custo
                custo_file = f"{dir_agente}/tour_cost.txt"
                custo = ler_custo_tour(custo_file)
                custos_agentes.append(custo)
                print(f"  [OK] Agente {i}: Custo = {custo:.2f}s ({custo/60:.2f} min)")
        
        # ===== PASSO 7: Gerar visualizações =====
        print_step(7, "Gerando visualizacoes")
        
        # Mapa individual para cada agente
        for i in range(num_agentes):
            dir_agente = os.path.join(DIR_RESULTADOS, f"agente_{i}")
            output_file = os.path.join(DIR_VISUALIZACOES, f"mapa_agente_{i}.html")
            
            executar_script(
                ["python", "codigo_fonte/visualizacao/visualizar_mapa_agente.py", 
                 str(i), dir_agente, output_file],
                f"Mapa do agente {i}"
            )
        
        # Mapa consolidado com todos os agentes
        print(f"\n  -> Gerando mapa consolidado com todos os {num_agentes} agentes...")
        
        # Gerar mapa consolidado diretamente
        output_consolidado = os.path.join(DIR_VISUALIZACOES, f"mapa_todos_{num_agentes}_agentes.html")
        
        # Criar script inline para gerar o mapa
        import pandas as pd
        import folium
        
        PATH_VERTICES = "dados_processados/vertices_reordenados.csv"
        vdf = pd.read_csv(PATH_VERTICES)
        coord = {int(r["id"]): (r["lat"], r["lon"]) for _, r in vdf.iterrows()}
        
        cores = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
        
        lat_media = vdf["lat"].mean()
        lon_media = vdf["lon"].mean()
        m = folium.Map(location=[lat_media, lon_media], zoom_start=15, tiles=None)
        
        # A BASE é sempre o vértice 0 (DEPOT_NODE)
        DEPOT_NODE = 0
        base_coord = coord.get(DEPOT_NODE)
        
        for agente_id in range(num_agentes):
            dir_agente = os.path.join(DIR_RESULTADOS, f"agente_{agente_id}")
            tour_file = os.path.join(dir_agente, "tour.csv")
            
            if not os.path.exists(tour_file):
                continue
            
            tdf = pd.read_csv(tour_file)
            tour = tdf["vertex"].tolist()
            
            if not tour:
                continue
            
            cor = cores[agente_id % len(cores)]
            fg = folium.FeatureGroup(name=f"Agente {agente_id}", show=True)
            
            polyline_coords = []
            for v in tour:
                if v in coord:
                    polyline_coords.append(coord[v])
            
            folium.PolyLine(
                locations=polyline_coords,
                weight=4,
                color=cor,
                tooltip=f"Agente {agente_id}",
                opacity=0.8
            ).add_to(fg)
            
            fg.add_to(m)
        
        # Adicionar marker da BASE (vértice 0)
        if base_coord:
            folium.Marker(
                location=base_coord,
                popup="BASE - Ponto de Partida e Retorno (Vertice 0)",
                icon=folium.Icon(color='blue', icon='home', prefix='fa'),
                tooltip="Base dos Agentes"
            ).add_to(m)
        
        esri_imagery_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        folium.TileLayer(tiles=esri_imagery_url, attr="Tiles © Esri", name="Esri WorldImagery", overlay=False, control=True).add_to(m)
        
        folium.LayerControl(position='topright', collapsed=False, autoZIndex=True).add_to(m)
        
        m.save(output_consolidado)
        print(f"  [OK] Mapa consolidado salvo: {output_consolidado}")
    
    else:
        # Um único agente
        print_step(5, "Modo de agente unico - usando tour completo")
        
        custo_file = os.path.join(DIR_TOUR, "tour_cost.txt")
        custo = ler_custo_tour(custo_file)
        custos_agentes.append(custo)
        print(f"  [OK] Custo total: {custo:.2f}s ({custo/60:.2f} min)")
        
        # ===== PASSO 6: Gerar visualizações =====
        print_step(6, "Gerando visualizacoes (mapas)")
        
        # Gerar mapa interativo diretamente
        output_mapa = os.path.join(DIR_VISUALIZACOES, "mapa_cpp.html")
        
        import pandas as pd
        import folium
        
        PATH_VERTICES = "dados_processados/vertices_reordenados.csv"
        tour_file = os.path.join(DIR_TOUR, "tour.csv")
        
        vdf = pd.read_csv(PATH_VERTICES)
        tdf = pd.read_csv(tour_file)
        
        coord = {int(r["id"]): (r["lat"], r["lon"]) for _, r in vdf.iterrows()}
        tour = tdf["vertex"].tolist()
        
        if tour:
            lat0, lon0 = coord[tour[0]]
            m = folium.Map(location=[lat0, lon0], zoom_start=16, tiles=None)
            
            # Adicionar rota
            polyline_coords = []
            for v in tour:
                if v in coord:
                    polyline_coords.append(coord[v])
            
            folium.PolyLine(
                locations=polyline_coords,
                weight=4,
                color="#00A3FF",
                tooltip="Caminho CPP"
            ).add_to(m)
            
            # Adicionar marker da BASE (vértice 0)
            DEPOT_NODE = 0
            if DEPOT_NODE in coord:
                folium.Marker(
                    location=coord[DEPOT_NODE],
                    popup="BASE - Ponto de Partida e Retorno (Vertice 0)",
                    icon=folium.Icon(color='blue', icon='home', prefix='fa'),
                    tooltip="Base do Agente"
                ).add_to(m)
            
            # Adicionar camada de satélite
            esri_imagery_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            folium.TileLayer(
                tiles=esri_imagery_url,
                attr="Tiles © Esri",
                name="Esri WorldImagery",
                overlay=False,
                control=True,
            ).add_to(m)
            
            folium.LayerControl().add_to(m)
            
            m.save(output_mapa)
            print(f"  [OK] Mapa salvo: {output_mapa}")
    
    # ===== PASSO 7/8: Calcular métricas finais =====
    passo_metricas = 8 if num_agentes > 1 else 7
    print_step(passo_metricas, "Calculando metricas finais e custos operacionais")
    
    # Salvar relatório na pasta correta
    relatorio_file_original = f"resultados_finais/relatorio_metricas_{num_agentes}_agentes.txt"
    relatorio_file = os.path.join(DIR_RESULTADOS, f"relatorio_metricas_{num_agentes}_agentes.txt")
    
    calcular_metricas(custos_agentes, num_agentes)
    
    # Mover relatório para pasta correta
    if os.path.exists(relatorio_file_original):
        import shutil
        shutil.move(relatorio_file_original, relatorio_file)
    
    # ===== PASSO FINAL: Gerar animações =====
    passo_animacao = passo_metricas + 1
    print_step(passo_animacao, "Gerando animacoes (ULTIMO PASSO - pode demorar)")
    
    if num_agentes > 1:
        # Animações para cada agente
        for i in range(num_agentes):
            dir_agente = os.path.join(DIR_RESULTADOS, f"agente_{i}")
            output_file = os.path.join(DIR_VISUALIZACOES, f"animacao_agente_{i}.mp4")
            
            print(f"\n  -> Agente {i}...")
            executar_script(
                ["python", "codigo_fonte/visualizacao/visualizar_animacao_agente.py",
                 str(i), dir_agente, output_file],
                f"Animacao do agente {i}"
            )
    else:
        # Animação única
        output_file = os.path.join(DIR_VISUALIZACOES, "animacao_cpp.mp4")
        print(f"\n  -> Gerando animacao...")
        executar_script(
            ["python", "codigo_fonte/visualizacao/visualizar_animacao_agente.py",
             "0", DIR_TOUR, output_file],
            "Animacao da rota"
        )
    
    # ===== FINALIZAÇÃO =====
    tempo_total = time.time() - inicio_total
    
    print_header("PIPELINE CONCLUIDO COM SUCESSO")
    print(f"Tempo total de execucao: {tempo_total:.2f}s ({tempo_total/60:.2f} min)")
    print(f"Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"\n[ARQUIVOS] Todos os resultados foram salvos em:")
    print(f"  -> {DIR_RESULTADOS}/")
    print(f"\n[CONTEUDO]")
    print(f"  * Grafos e imagens: {DIR_RESULTADOS}/")
    print(f"  * Mapas interativos: {DIR_VISUALIZACOES}/")
    print(f"  * Animacoes (MP4): {DIR_VISUALIZACOES}/")
    print(f"  * Relatorio de metricas: {DIR_RESULTADOS}/relatorio_metricas_{num_agentes}_agentes.txt")
    if num_agentes > 1:
        print(f"  * Tours por agente: {DIR_RESULTADOS}/agente_X/")
        print(f"  * Clusters: dados_processados/clusters_finais/")
    print()

if __name__ == "__main__":
    main()
