#Calcula o peso das arestas em segundos considerando a distância percorrida por uma pessoa a pé e o tempo de serviço para cada casa da rua


import pandas as pd

# Arquivo de entrada
ARQUIVO_ENTRADA = "dados_processados/arestas_calc_com_casas.csv"

# Arquivo de saída
ARQUIVO_SAIDA = "dados_processados/arestas_com_peso_final.csv"

# Velocidade média de caminhada (m/s)
VELOCIDADE = 1.4  # 1,4 metros por segundo

# Tempo por casa (segundos)
TEMPO_POR_CASA = 20

# ------------------------------------------------------

# Carregar arquivo
df = pd.read_csv(ARQUIVO_ENTRADA)

# Garantir que as colunas existam
esperadas = ["origem", "destino", "distancia_m", "numero_de_casas"]
for coluna in esperadas:
    if coluna not in df.columns:
        raise ValueError(f"Coluna obrigatória ausente: {coluna}")

# Calcular tempo a pé
df["tempo_a_pe_s"] = df["distancia_m"] / VELOCIDADE

# Calcular tempo de atendimento
df["tempo_casas_s"] = df["numero_de_casas"] * TEMPO_POR_CASA

# Peso total
df["peso"] = df["tempo_a_pe_s"] + df["tempo_casas_s"]

# Montar CSV final (somente colunas desejadas)
df_saida = df[["origem", "destino", "peso"]]

# Salvar
df_saida.to_csv(ARQUIVO_SAIDA, index=False)

print("Gerado:", ARQUIVO_SAIDA)
