# 🗺️ Pipeline de Otimização de Rotas para Coleta de Dados Imobiliários

Sistema automatizado para otimização de rotas de coleta de dados imobiliários usando o Problema do Carteiro Chinês (CPP).

## 📋 Descrição

Este projeto resolve o problema de planejamento de rotas para agentes de coleta de dados imobiliários em campo. O sistema:

- Calcula rotas otimizadas considerando distância e tempo de serviço
- Suporta múltiplos agentes trabalhando simultaneamente
- Gera visualizações interativas (mapas HTML) e animações (vídeos MP4)
- Calcula métricas de tempo e custos operacionais
- Organiza resultados em pastas sequenciais

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalar Dependências

```bash
pip install -r requirements.txt
```

## 📊 Dados de Entrada

O sistema requer dois arquivos CSV em `dados_processados/`:

1. **vertices_reordenados.csv**: Lista de vértices com coordenadas
   ```csv
   id,lat,lon
   0,-21.6097503,-45.5672034
   1,-21.6095123,-45.5670123
   ...
   ```

2. **arestas_calc_com_casas.csv**: Arestas com distâncias e número de casas
   ```csv
   origem,destino,distancia_m,numero_de_casas
   0,1,150.5,12
   1,2,200.3,15
   ...
   ```

## 🎯 Uso

### Execução Básica

```bash
python main.py <num_agentes>
```

### Exemplos

**Um único agente:**
```bash
python main.py 1
```

**Dois agentes:**
```bash
python main.py 2
```

**Três agentes:**
```bash
python main.py 3
```

### Modo Interativo

Execute sem argumentos para modo interativo:
```bash
python main.py
```

## 📁 Estrutura de Saída

Os resultados são salvos em pastas sequenciais:

```
resultados/
├── grafo-1/          # Primeira execução
│   ├── visualizacoes/
│   │   ├── mapa_agente_0.html
│   │   ├── mapa_agente_1.html
│   │   ├── mapa_todos_2_agentes.html
│   │   ├── animacao_agente_0.mp4
│   │   └── animacao_agente_1.mp4
│   ├── agente_0/
│   │   ├── tour.csv
│   │   ├── tour_cost.txt
│   │   ├── tour_detalhado.csv
│   │   └── matching_paths.csv
│   ├── agente_1/
│   ├── relatorio_tour/
│   └── relatorio_metricas_2_agentes.txt
├── grafo-2/          # Segunda execução
└── grafo-3/          # Terceira execução
```

## 🔄 Pipeline de Processamento

O sistema executa automaticamente os seguintes passos:

1. **Calcular Pesos**: Combina distância e tempo de serviço por casa
2. **Gerar Matriz**: Cria matriz de adjacência do grafo
3. **Visualizar Grafo**: Gera imagem estática do grafo
4. **Resolver CPP**: Encontra o circuito Euleriano ótimo
5. **Dividir Clusters**: Divide o trabalho entre N agentes (se N > 1)
6. **Resolver CPP por Agente**: Otimiza a rota de cada agente
7. **Gerar Mapas**: Cria mapas interativos HTML
8. **Calcular Métricas**: Analisa tempo e custos
9. **Gerar Animações**: Cria vídeos MP4 das rotas

## 📊 Métricas Calculadas

O sistema calcula automaticamente:

- ⏱️ Tempo de trabalho por agente (minutos e horas)
- 💰 Custo operacional por agente (R$/hora configurável)
- 📈 Comparação: 1 agente vs N agentes
- 💡 Economia de tempo percentual
- 📅 Dias de trabalho necessários

## ⚙️ Configurações

Edite `main.py` para ajustar:

```python
CUSTO_HORA_AGENTE = 50.0      # R$/hora
HORAS_TRABALHO_DIA = 8        # horas/dia
VELOCIDADE_CAMINHADA = 1.4    # m/s
TEMPO_POR_CASA = 20           # segundos
```

## 🗺️ Visualizações

### Mapas Interativos (HTML)
- Abra no navegador para explorar as rotas
- Camadas de satélite (Esri WorldImagery)
- Controles interativos para mostrar/ocultar rotas
- Marker azul indica a BASE (ponto de partida/retorno)

### Animações (MP4)
- Vídeos mostrando a rota sendo percorrida
- Uma animação por agente
- Útil para apresentações

## 📝 Arquivos do Projeto

### Raiz
- `main.py` - Pipeline principal
- `calcular_peso_com_casas.py` - Cálculo de pesos
- `route2.py` - Divisão em clusters
- `requirements.txt` - Dependências

### codigo_fonte/
- `algoritmo_cpp/resolver_cpp.py` - Algoritmo CPP (Edmonds-Johnson)
- `setup_grafo/gerar_matriz_adjacencia.py` - Geração de matriz
- `visualizacao/visualizar_grafo_estatico.py` - Grafo estático
- `visualizacao/visualizar_mapa_agente.py` - Mapas individuais
- `visualizacao/visualizar_animacao_agente.py` - Animações

### dados_processados/
- `vertices_reordenados.csv` - Entrada: vértices
- `arestas_calc_com_casas.csv` - Entrada: arestas
- `arestas_com_peso_final.csv` - Gerado: pesos calculados
- `matriz_adjacencia.csv` - Gerado: matriz do grafo
- `clusters_finais/` - Gerado: matrizes por agente

## 🔧 Troubleshooting

### Erro: "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Animações não são geradas
Certifique-se de que `contextily` e `moviepy` estão instalados:
```bash
pip install contextily moviepy
```

## 📖 Algoritmo

O sistema usa o **Algoritmo de Edmonds-Johnson** para resolver o Problema do Carteiro Chinês:

1. Identifica vértices de grau ímpar
2. Calcula caminhos mínimos (Dijkstra)
3. Encontra emparelhamento perfeito de custo mínimo
4. Constrói multigrafo aumentado
5. Extrai circuito Euleriano (Hierholzer)

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos.

## 👥 Contexto

Projeto desenvolvido para otimização de coleta de dados no Recadastramento Imobiliário Multifinalitário Georreferenciado da cidade de Elói Mendes/MG.

## 📊 Resultados de Exemplo

### Mapas Interativos Gerados

Clique nos links abaixo para visualizar os mapas interativos:

#### [🗺️ Mapa com 1 Agente](assets/mapas/mapa_1_agente.html)
- **Tempo**: 12.94 horas (1.62 dias)
- **Custo**: R$ 647.08
- Rota completa em azul

#### [🗺️ Mapa com 2 Agentes](assets/mapas/mapa_2_agentes.html)
- **Tempo Paralelo**: 6.69 horas (0.84 dias)
- **Economia**: 49.3% de tempo
- **Custo**: R$ 669.21 (+1.4%)
- Rotas: Vermelho (Agente 0) e Verde (Agente 1)

#### [🗺️ Mapa com 3 Agentes](assets/mapas/mapa_3_agentes.html)
- **Tempo Paralelo**: 5.32 horas (0.66 dias)
- **Economia**: 63.3% de tempo
- **Custo**: R$ 797.55 (+10.2%)
- Rotas: Vermelho (Agente 0), Verde (Agente 1) e Azul (Agente 2)

### Análise Comparativa

| Cenário | Tempo (horas) | Dias Úteis | Custo (R$) | Economia Tempo |
|---------|---------------|------------|------------|----------------|
| 1 Agente | 12.94 | 1.62 | 647.08 | - |
| 2 Agentes | 6.69 | 0.84 | 669.21 | 49.3% |
| 3 Agentes | 5.32 | 0.66 | 797.55 | 63.3% |

**Conclusão**: Com 2 agentes, reduz-se quase metade do tempo com apenas 1.4% de custo adicional. Com 3 agentes, a economia de tempo é de 63%, mas o custo aumenta 10%.

## 🖼️ Imagens

Veja a pasta `assets/` para imagens da área de estudo.
