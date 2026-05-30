# Processamento de Sinais em Espectros FTIR de Vinhos

Projeto da disciplina de **Análise de Sinais e Sistemas** para processar e interpretar espectros de infravermelho por Transformada de Fourier (**FTIR**) de vinhos tintos Cabernet Sauvignon e Shiraz.

O objetivo é tratar cada espectro como um **sinal discreto**, reduzir ruído experimental, aplicar filtros digitais, isolar bandas químicas e extrair métricas comparáveis entre amostras.

---

## Ideia Central

O arquivo de entrada já contém espectros FTIR no domínio do número de onda. Assim, o eixo horizontal não é tempo, mas pode ser modelado como um índice discreto:

$$
x[n] = \text{absorbância no número de onda associado ao índice } n
$$

Cada sinal medido é interpretado como:

$$
x[n] = v[n] + e[n]
$$

onde `v[n]` representa a informação química do vinho e `e[n]` representa ruído experimental.

O pipeline implementado é:

**dados brutos → média das triplicatas → filtros de suavização → passa-bandas químicos → pico/área → comparação entre vinhos**

---

## Dados

O conjunto principal está em:

- `data/Wine_FTIR_Triplicate_Spectra.csv`

Características:

- 37 vinhos únicos;
- 3 medições por vinho, totalizando 111 espectros;
- 235 pontos por espectro;
- faixa aproximada de 899 a 1803 cm^-1;
- variedades Cabernet Sauvignon e Shiraz.

A região analisada corresponde à chamada região de impressão digital do infravermelho, na qual bandas de absorção ajudam a diferenciar grupos químicos.

---

## Metodologia

### 1. Carregamento e modelagem

A função `load_data()` lê o CSV e usa `Wavenumbers` como índice do `DataFrame`.

O espectro passa a ser tratado como sequência discreta de absorbâncias.

### 2. Média das triplicatas

A função `calc_mean()` agrupa as três réplicas de cada vinho e calcula:

$$
y_{\text{mean}}[n] = \frac{x_1[n] + x_2[n] + x_3[n]}{3}
$$

Essa etapa aplica linearidade/superposição para reduzir ruído aleatório entre medições.

### 3. Filtros de suavização

Foram comparadas duas estratégias:

- `dsp_filter()`: filtro **Savitzky-Golay**, com janela 11 e polinômio de ordem 2;
- `dsp_filter_moving_average()`: filtro de **média móvel FIR**, implementado por convolução discreta.

A média móvel é simples e reduz ruído, mas pode achatar picos. O Savitzky-Golay preserva melhor a forma, altura e largura dos picos espectrais, por isso é usado como referência principal nos gráficos finais.

### 4. Passa-bandas químicos

A função `extract_wine_metrics()` isola regiões por máscaras no eixo de número de onda. Essas máscaras equivalem a filtros passa-banda ideais aplicados sobre o espectro suavizado.

Faixas usadas:

| Composto | Faixa aproximada |
|---|---:|
| Açúcares / carboidratos | 900 a 1150 cm^-1 |
| Ácidos orgânicos | 1160 a 1240 cm^-1 |
| Polifenóis / taninos | 1400 a 1600 cm^-1 |
| Proteínas / amidas | 1600 a 1700 cm^-1 |
| Ésteres / aromas | 1730 a 1750 cm^-1 |

### 5. Métricas extraídas

Para cada banda são calculadas:

- **pico mais proeminente**, via `get_main_peak()` e `scipy.signal.find_peaks`;
- **área integrada da banda**, via `np.trapezoid()`.

A área funciona como uma integração discreta no eixo espectral e pode ser interpretada como energia/concentração relativa da banda.

---

## Estrutura do Projeto

```text
.
├── data/                  # Dados FTIR e janelas/faixas químicas
├── images/                # Fluxogramas usados na apresentação
├── notebooks/             # Notebook exploratório
├── results/               # CSVs e gráficos gerados
├── src/
│   ├── main.py            # Pipeline principal
│   ├── utils.py           # Funções de leitura, filtros, métricas e gráficos
│   ├── raw_charts.py      # Gráficos de pontos das réplicas brutas
│   ├── sqsignals.py       # Visualização de passa-bandas
│   └── concentration.py   # Apoio para gráficos de concentração/assinatura
├── DESCRICAO_GRAFICOS.md  # Explicação dos gráficos gerados
├── DISCUSSION.md          # Discussão conceitual inicial
├── RELATORIO_BASE.md      # Base teórica detalhada
└── SUGESTAO_APRESENTACAO.md
```

---

## Como Executar

Crie um ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Execute o pipeline principal a partir da pasta `src`, pois alguns scripts usam caminhos relativos para `../data` e `../results`:

```bash
cd src
python main.py
```

Scripts úteis:

```bash
cd src
python raw_charts.py      # Mostra gráficos de pontos das réplicas brutas
python sqsignals.py       # Mostra os passa-bandas sobre os espectros
```

Observação: os scripts usam `matplotlib.pyplot.show()`, então a execução pode abrir janelas de gráficos e aguardar que elas sejam fechadas.

Os gráficos de concentração e assinatura espectral em `results/` são gerados a partir das funções `statistics()`, `plot_bar_charts()`, `scatter_plot()` e `plot_radar_chart()` em `src/utils.py`.

---

## Reproduzindo pelo Notebook

O notebook principal para replicação completa é:

- `notebooks/analise.ipynb`

Ele foi organizado em blocos separados para:

1. configurar caminhos e importar funções;
2. carregar o CSV bruto;
3. gerar gráficos dos dados iniciais como pontos;
4. calcular a média das triplicatas;
5. comparar Savitzky-Golay e média móvel;
6. extrair métricas por bandas químicas;
7. gerar passa-bandas, barras, dispersão e radar;
8. salvar os CSVs e PNGs na pasta `results/`.

Para executar:

```bash
source .venv/bin/activate
jupyter lab notebooks/analise.ipynb
```

ou:

```bash
source .venv/bin/activate
jupyter notebook notebooks/analise.ipynb
```

Depois, use **Run All Cells**. O notebook detecta automaticamente se foi aberto pela raiz do projeto ou pela pasta `notebooks/`, então os caminhos para `data/`, `src/` e `results/` são configurados dentro da primeira célula de código.

Ao final da execução, os principais gráficos e tabelas são atualizados em `results/`.

---

## Principais Saídas

Arquivos CSV:

- `results/savitzky_golay_corrigido.csv`
- `results/media_movel_corrigido.csv`

Gráficos principais:

- `results/dados_iniciais_wine_01_rep1.png`: dados brutos como pontos discretos;
- `results/wine_01_media_triplicata.png`: comparação das triplicatas e média;
- `results/wine_01.png`: comparação entre sinal bruto, média móvel e Savitzky-Golay;
- `results/passa_bandas_degraus_unitarios.png`: regiões químicas isoladas por passa-bandas;
- `results/concentracao_compostos_sg.png`: assinatura média Cabernet vs Shiraz;
- `results/espaco_separacao_sg.png`: dispersão polifenóis vs aromas;
- `results/identidade_espectral.png`: radar da identidade espectral média.

Resumo dos resultados:

- os filtros Savitzky-Golay e média móvel geraram áreas médias muito próximas;
- o Savitzky-Golay preservou melhor a forma dos picos;
- Cabernet e Shiraz ficaram próximos nas métricas médias das bandas escolhidas;
- as métricas extraídas são úteis como assinatura espectral, mas não separam perfeitamente as variedades sozinhas.

---

## Materiais de Apoio

- `SUGESTAO_APRESENTACAO.md`: roteiro sugerido para apresentação de 15 minutos;
- `DESCRICAO_GRAFICOS.md`: finalidade e interpretação de cada gráfico;
- `RELATORIO_BASE.md`: fundamentação teórica mais completa;
- `DISCUSSION.md`: discussão conceitual e conexão com Sinais e Sistemas.

---

## Fonte dos Dados

Os dados utilizados foram obtidos do repositório [Wine_Cabernet_Shiraz_FTIR](https://github.com/QIBChemometrics/Wine_Cabernet_Shiraz_FTIR), do Quadram Institute Bioscience, sob licença CC0 1.0 Universal.

**Referência acadêmica:**  
Kemsley EK, Defernez M, Marini F. (2019). *Multivariate statistics: Considerations and confidences in food authenticity problems*. Food Control, 105, 102-112.
