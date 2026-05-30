
import pandas as pd
import os
from scipy.signal import savgol_filter, find_peaks
import numpy as np
import matplotlib.pyplot as plt

base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, '../data/Wine_FTIR_Triplicate_Spectra.csv')


def load_data(file_path):
    """Opens a CSV file with spectral wavenumbers data using Pandas and 
    makes sure the index is selected as the Wavenumbers column
    Returns a DataFrame.
    
    Args:
        file_path : string with the .csv file
        df : Pandas DataFrama object with the data on the csv file"""
    
    df = pd.read_csv(file_path)
    df.set_index('Wavenumbers', inplace=True)

    return df

def load_results(csv_path, index_tags):
    """Opens a CSV file with spectral wavenumbers data using Pandas and 
    makes sure the index is selected as the Wavenumbers column
    Returns a DataFrame.
    
    Args:
        file_path : string with the .csv file
        df : Pandas DataFrama object with the data on the csv file"""
    

    df = pd.read_csv(csv_path, index_tags)
    # df_sg = pd.read_csv('../results/savitzky_golay_corrigido.csv')
    
    df.index = index_tags
    df['Uva'] = ['Cabernet' if 'Cab' in nome else 'Shiraz' for nome in df.index]

    return df

def calc_mean(df):
    """
    Aplica o Princípio da Superposição em Sistemas Lineares.
    Agrupa as colunas por vinho e calcula a média das triplicatas, 
    atuando como um cancelador de ruído aleatório (média zero) para 
    reforçar o sinal determinístico.

    Agrupa as colunas por vinho (ex: Wine_01) e calcula a média das triplicatas.
    Retorna um DataFrame onde cada coluna é um vinho único.
    """

    wine_tags = [col.rsplit('_', 1)[0] for col in df.columns]
    df_mean = df.groupby(wine_tags, axis=1).mean()
    return df_mean

def plot_raw_triplicate_scatter(df_triplicata, wine_column=None, title=None, show=True):
    """
    Gera um grafico de pontos para uma unica replicata de um vinho.

    A entrada pode ser:
    - uma Series com indice Wavenumbers;
    - um DataFrame com uma unica coluna espectral;
    - um DataFrame contendo a coluna Wavenumbers e uma unica coluna espectral.
    """

    if isinstance(df_triplicata, pd.Series):
        serie = df_triplicata
    else:
        df_plot = df_triplicata.copy()

        if 'Wavenumbers' in df_plot.columns:
            df_plot = df_plot.set_index('Wavenumbers')

        if wine_column is not None:
            serie = df_plot[wine_column]
        else:
            if len(df_plot.columns) != 1:
                raise ValueError(
                    "Informe wine_column ou passe um DataFrame com uma unica coluna espectral."
                )
            serie = df_plot.iloc[:, 0]

    label = serie.name if serie.name is not None else 'Triplicata'
    plot_title = title or f'Dados Brutos Iniciais - {label}'

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(
        serie.index,
        serie.values,
        label=label,
        color='tab:blue',
        s=28,
        alpha=0.8,
        edgecolors='none'
    )

    ax.set_title(plot_title, fontsize=14)
    ax.set_xlabel('Wavenumbers ($cm^{-1}$)', fontsize=12)
    ax.set_ylabel('Absorbância', fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend()
    fig.tight_layout()

    if show:
        plt.show()

    return fig, ax

def dsp_filter(serie_sinal, janela=11, ordem=2):
    """Aplica o filtro Savitzky-Golay (Filtro FIR avançado).
    Preserva a altura e a forma dos picos espectrais."""
    
    return pd.Series(
        savgol_filter(serie_sinal, window_length=janela, polyorder=ordem),
        index=serie_sinal.index
    )

def dsp_filter_moving_average(serie_sinal, janela=5):
    """
    Implementa um Filtro Passa-Baixas FIR (Média Móvel) do zero.
    
    Teoria:
    1. Define a resposta ao impulso h[n] como um pulso retangular.
    2. Aplica o sistema SLIT-D (Sistema Linear Invariante no Tempo Discreto)
       através da Soma de Convolução: y[n] = x[n] * h[n].
    """
    # 1. Construindo a resposta ao impulso h[n]
    h_n = np.ones(janela) / janela 
    
    # 2. Aplicando a Convolução Discreta (x[n] * h[n])
    # mode='same' garante que o sinal de saída mantenha os mesmos 235 pontos
    sinal_filtrado = np.convolve(serie_sinal, h_n, mode='same')
    
    # Retornamos como Pandas Series para preservar o eixo X (Wavenumbers)
    return pd.Series(sinal_filtrado, index=serie_sinal.index)

def get_main_peak(segmento):
    """
    Retorna o pico mais proeminente de uma região espectral.
    Evita pegar baseline alto como 'pico'.
    """
    if segmento.empty:
        return 0.0

    # Detecta picos locais
    indices, props = find_peaks(
        segmento,
        prominence=0.01  # ajustar empiricamente
    )

    # Se não achou pico, fallback para máximo
    if len(indices) == 0:
        return segmento.max()

    # Escolhe o pico mais proeminente
    pico_idx = indices[np.argmax(props["prominences"])]

    return segmento.iloc[pico_idx]

def extract_wine_metrics(serie_filtrada):

    metrics = {
        'pico_acucar': 0.0, 'area_acucar': 0.0,
        'pico_aroma': 0.0, 'area_aroma': 0.0,
        'pico_polifenois': 0.0, 'area_polifenois': 0.0,
        'pico_proteinas': 0.0, 'area_proteinas': 0.0,
        'pico_acidos': 0.0, 'area_acidos': 0.0
    }

    # Aroma
    mask_aroma = (serie_filtrada.index >= 1730) & (serie_filtrada.index <= 1750)
    segmento_aroma = serie_filtrada[mask_aroma]

    if not segmento_aroma.empty:
        metrics['pico_aroma'] = get_main_peak(segmento_aroma)
        metrics['area_aroma'] = np.trapezoid(
            segmento_aroma.values,
            x=segmento_aroma.index
        )

    # Açúcar
    mask_acucar = (serie_filtrada.index >= 900) & (serie_filtrada.index <= 1150)
    segmento_acucar = serie_filtrada[mask_acucar]

    if not segmento_acucar.empty:
        metrics['pico_acucar'] = get_main_peak(segmento_acucar)
        metrics['area_acucar'] = np.trapezoid(
            segmento_acucar.values,
            x=segmento_acucar.index
        )

    # Polifenóis
    mask_polifenois = (serie_filtrada.index >= 1400) & (serie_filtrada.index <= 1600)
    segmento_polifenois = serie_filtrada[mask_polifenois]

    if not segmento_polifenois.empty:
        metrics['pico_polifenois'] = get_main_peak(segmento_polifenois)
        metrics['area_polifenois'] = np.trapezoid(
            segmento_polifenois.values,
            x=segmento_polifenois.index
        )

    # Proteínas
    mask_proteinas = (serie_filtrada.index >= 1600) & (serie_filtrada.index <= 1700)
    segmento_proteinas = serie_filtrada[mask_proteinas]

    if not segmento_proteinas.empty:
        metrics['pico_proteinas'] = get_main_peak(segmento_proteinas)
        metrics['area_proteinas'] = np.trapezoid(
            segmento_proteinas.values,
            x=segmento_proteinas.index
        )

    # Ácidos
    mask_acidos = (serie_filtrada.index >= 1160) & (serie_filtrada.index <= 1240)
    segmento_acidos = serie_filtrada[mask_acidos]

    if not segmento_acidos.empty:  # <- bug corrigido
        metrics['pico_acidos'] = get_main_peak(segmento_acidos)
        metrics['area_acidos'] = np.trapezoid(
            segmento_acidos.values,
            x=segmento_acidos.index
        )

    return metrics

def extract_wine_metrics_old(serie_filtrada):
    """
    Identifica picos específicos e calcula a área sob a curva.
    SINAIS E SISTEMAS:
    A integração (np.trapz) atua como um sistema Acumulador discreto 
    y[n] = y[n-1] + x[n], calculando a "Energia" ou concentração do composto.
    """
    # 1. Achar todos os picos do sinal
    indices_picos, _ = find_peaks(serie_filtrada, height=0.02)
    wavenumbers_picos = serie_filtrada.index[indices_picos]
    
    # Dicionário para guardar os resultados do vinho
    metrics = {
        'pico_acucar': 0.0, 'area_acucar': 0.0,
        'pico_aroma': 0.0, 'area_aroma': 0.0,
        'pico_polifenois': 0.0, 'area_polifenois': 0.0,
        'pico_proteinas': 0.0, 'area_proteinas': 0.0,
        'pico_acidos': 0.0, 'area_acidos': 0.0
    }

    # 2. Lógica para identificar e calcular áreas
    # Região Açúcar: 900 - 1150
    # Região Aroma (Ésteres): 1730 - 1750
    
    # Aroma (Ésteres):
    mask_aroma = (serie_filtrada.index >= 1730) & (serie_filtrada.index <= 1750)
    segmento_aroma = serie_filtrada[mask_aroma]
    if not segmento_aroma.empty:
        metrics['pico_aroma'] = segmento_aroma.max()
        # Regra do Trapézio para Integral (Concentração)
        metrics['area_aroma'] = np.trapezoid(segmento_aroma.values, x=segmento_aroma.index)
        
    # Açúcar:
    mask_acucar = (serie_filtrada.index >= 900) & (serie_filtrada.index <= 1150)
    segmento_acucar = serie_filtrada[mask_acucar]
    if not segmento_acucar.empty:
        metrics['pico_acucar'] = segmento_acucar.max()
        # Regra do Trapézio para Integral (Concentração)
        metrics['area_acucar'] = np.trapezoid(segmento_acucar.values, x=segmento_acucar.index)
    
    # Polifenois:
    mask_polifenois = (serie_filtrada.index >= 1400) & (serie_filtrada.index <= 1600)
    segmento_polifenois = serie_filtrada[mask_polifenois]
    if not segmento_polifenois.empty:
        metrics['pico_polifenois'] = segmento_polifenois.max()
        metrics['area_polifenois'] = np.trapezoid(segmento_polifenois.values, x=segmento_polifenois.index)
    
    # Proteínas:
    mask_proteinas = (serie_filtrada.index >= 1600) & (serie_filtrada.index <= 1700)
    segmento_proteinas = serie_filtrada[mask_proteinas]
    if not segmento_proteinas.empty:
        metrics['pico_proteinas'] = segmento_proteinas.max()
        metrics['area_proteinas'] = np.trapezoid(segmento_proteinas.values, x=segmento_proteinas.index)
    
    # Ácidos Organicos (1200 cm-1): 
    mask_acidos = (serie_filtrada.index >= 1160) & (serie_filtrada.index <= 1240)
    segmento_acidos = serie_filtrada[mask_acidos]
    if not segmento_polifenois.empty:
        metrics['pico_acidos'] = segmento_acidos.max()
        metrics['area_acidos'] = np.trapezoid(segmento_acidos.values, x=segmento_acidos.index)

    return metrics


# Função para comparar filtros
def compare_filters(df, df_mean, wine_column='Wine_01'):
    """
    Gera um gráfico comparando o sinal bruto, o filtro Savitzky-Golay
    e o filtro de Média Móvel (Convolução) para um vinho específico.
    """

    sinal_bruto = df_mean[wine_column]
    
    # Aplica os dois filtros
    sinal_savgol = dsp_filter(sinal_bruto, janela=11, ordem=2)
    sinal_convolucao = dsp_filter_moving_average(sinal_bruto, janela=7) # Janela 7 para visualização clara
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df[f"{wine_column}_Rep1"], label='Réplica 1 (Bruto)', color='green', linewidth=2, linestyle='-')

    # plt.plot(sinal_bruto.index, sinal_bruto.values, label='Média das Triplicatas (ruídos anulados)', alpha=0.4, color='green')
    plt.plot(sinal_savgol.index, sinal_savgol.values, label='Filtro Savitzky-Golay (Ideal para Picos)', linewidth=2, color='blue')
    plt.plot(sinal_convolucao.index, sinal_convolucao.values, label='Média Móvel via Convolução (FIR)', linewidth=2, color='red', linestyle='--')
    
    plt.title(f'Comparação de Filtros SLIT-D - {wine_column}', fontsize=14)
    plt.xlabel('Wavenumbers ($cm^{-1}$)', fontsize=12)
    plt.ylabel('Absorbância', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()

def highlight_triple_avg(df, df_mean, wine_column='Wine_01'):
    """
    Gera um gráfico comparando o sinal cru com a média das triplicatas.
    """

    sinal_bruto = df_mean[wine_column]
    
    # plota dados crus
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df[f"{wine_column}_Rep1"], label='Réplica 1', color='blue', linewidth=2, linestyle='-')
    plt.plot(df.index, df[f"{wine_column}_Rep2"], label='Réplica 2', color='black', linewidth=2, linestyle='-')
    plt.plot(df.index, df[f"{wine_column}_Rep3"], label='Réplica 3', color='green', linewidth=2, linestyle='-')

    # plota média das triplicatas
    plt.plot(sinal_bruto.index, sinal_bruto.values, label='Média das Triplicatas (ruídos anulados)', color='red', linestyle='--')
    
    plt.title(f'Comparação de Dados Crus e Média das Triplicatas - {wine_column}', fontsize=14)
    plt.xlabel('Wavenumbers ($cm^{-1}$)', fontsize=12)
    plt.ylabel('Absorbância', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_pass_band(wine_name):
    
    # 1. Carregar espectro real de um vinho como fundo
    df_bruto = load_data(file_path)
    df_mean = calc_mean(df_bruto)
    sinal_vinho = dsp_filter(df_mean[wine_name]) # Sinal limpo para referência

    # 2. Carregar as 5 janelas que foram geradas
    # component_window = pd.read_csv(square_signal).set_index('Wavenumbers')
    j_acucar = pd.read_csv('../data/ftir_acucares.csv').set_index('Wavenumbers')
    j_acidos = pd.read_csv('../data/ftir_acidos_organicos.csv').set_index('Wavenumbers')
    j_polifenois = pd.read_csv('../data/ftir_polifenois.csv').set_index('Wavenumbers')
    j_proteinas = pd.read_csv('../data/ftir_proteinas.csv').set_index('Wavenumbers')
    j_esteres = pd.read_csv('../data/ftir_esteres.csv').set_index('Wavenumbers')

    # 3. Plotagem do Gráfico Comparativo
    plt.figure(figsize=(14, 7))

    # Espectro do Vinho em cinza ao fundo
    plt.plot(sinal_vinho.index, sinal_vinho.values, label='Sinal de Absorbancia com Filtro SG', color='black', alpha=0.5, linewidth=1.5)

    # Sobrepor as Janelas de Degraus Unitários (multiplicadas por um fator para escala visual, ex: 0.5)
    escala = 1
    # plt.fill_between(component_window.index, component_window['Janela_Degrau'] * escala, alpha=0.3, label=f'Filtro Passa-Banda: {component}', color='black')

    plt.plot(j_acucar.index, j_acucar['Absorbance'] * escala, label='Filtro Passa-Banda: Açúcares', color='blue', linewidth=2)
    plt.plot(j_acidos.index, j_acidos['Absorbance'] * escala, label='Filtro Passa-Banda: Ácidos Órg.', color='green', linewidth=2)
    plt.plot(j_polifenois.index, j_polifenois['Absorbance'] * escala, label='Filtro Passa-Banda: Polifenóis', color='red', linewidth=2)
    plt.plot(j_proteinas.index, j_proteinas['Absorbance'] * escala, label='Filtro Passa-Banda: Proteínas', color='purple', linewidth=2)
    plt.plot(j_esteres.index, j_esteres['Absorbance'] * escala, label='Filtro Passa-Banda: Ésteres (Aroma)', color='orange', linewidth=2)

    # Estética de Sinais e Sistemas
    plt.title('Mapeamento Espectral: Filtros Passa-Banda Ideais via Degrau Unitário Deslocado', fontsize=14)
    plt.xlabel('Frequência Espacial / Número de Onda (Wavenumbers - $cm^{-1}$)', fontsize=12)
    plt.ylabel('Amplitude (Absorbância / Ganho do Filtro)', fontsize=12)
    plt.xlim(sinal_vinho.index.min(), sinal_vinho.index.max())
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(alpha=0.2)

    plt.tight_layout()
    plt.show()

def plot_pass_band_all():
    
    # 1. Carregar espectro real de um vinho como fundo
    df_bruto = load_data(file_path)
    df_mean = calc_mean(df_bruto)
    sinal_vinho_1 = dsp_filter(df_mean["Wine_01_Cab"]) # Sinal limpo para referência
    sinal_vinho_2 = dsp_filter(df_mean["Wine_15_Syr"])

    # 2. Carregar as 5 janelas que foram geradas
    # component_window = pd.read_csv(square_signal).set_index('Wavenumbers')
    j_acucar = pd.read_csv('../data/ftir_acucares.csv').set_index('Wavenumbers')
    j_acidos = pd.read_csv('../data/ftir_acidos_organicos.csv').set_index('Wavenumbers')
    j_polifenois = pd.read_csv('../data/ftir_polifenois.csv').set_index('Wavenumbers')
    j_proteinas = pd.read_csv('../data/ftir_proteinas.csv').set_index('Wavenumbers')
    j_esteres = pd.read_csv('../data/ftir_esteres.csv').set_index('Wavenumbers')

    # 3. Plotagem do Gráfico Comparativo
    plt.figure(figsize=(14, 7))

    # Espectro do Vinho em cinza ao fundo
    plt.plot(sinal_vinho_1.index, sinal_vinho_1.values, label='Garrafa 1 Cabernet Sauvignon', color='black', alpha=0.5, linewidth=1.5, linestyle='-')
    plt.plot(sinal_vinho_2.index, sinal_vinho_2.values, label='Garrafa 15 Shiraz', color='black', alpha=0.5, linewidth=1.5, linestyle='--')

    # Sobrepor as Janelas de Degraus Unitários (multiplicadas por um fator para escala visual, ex: 0.5)
    escala = 1
    # plt.fill_between(component_window.index, component_window['Janela_Degrau'] * escala, alpha=0.3, label=f'Filtro Passa-Banda: {component}', color='black')

    plt.plot(j_acucar.index, j_acucar['Absorbance'] * escala, label='Filtro Passa-Banda: Açúcares', color='blue', linewidth=2)
    plt.plot(j_acidos.index, j_acidos['Absorbance'] * escala, label='Filtro Passa-Banda: Ácidos Órg.', color='green', linewidth=2)
    plt.plot(j_polifenois.index, j_polifenois['Absorbance'] * escala, label='Filtro Passa-Banda: Polifenóis', color='red', linewidth=2)
    plt.plot(j_proteinas.index, j_proteinas['Absorbance'] * escala, label='Filtro Passa-Banda: Proteínas', color='purple', linewidth=2)
    plt.plot(j_esteres.index, j_esteres['Absorbance'] * escala, label='Filtro Passa-Banda: Ésteres (Aroma)', color='orange', linewidth=2)

    # Estética de Sinais e Sistemas
    plt.title('Mapeamento Espectral: Filtros Passa-Banda Ideais via Degrau Unitário Deslocado', fontsize=14)
    plt.xlabel('Frequência Espacial / Número de Onda (Wavenumbers - $cm^{-1}$)', fontsize=12)
    plt.ylabel('Amplitude (Absorbância / Ganho do Filtro)', fontsize=12)
    plt.xlim(sinal_vinho_1.index.min(), sinal_vinho_1.index.max())
    plt.xlim(sinal_vinho_2.index.min(), sinal_vinho_2.index.max())
    plt.legend(loc='lower right', fontsize=7)
    plt.grid(alpha=0.2)

    plt.tight_layout()
    plt.show()

def statistics(column_list, df, group_by='Uva'):
    df_medias = df.groupby(group_by)[column_list].mean()

    return df_medias

def plot_bar_charts(df_medias):

    # ==============================================================================
    # VISUALIZAÇÃO DE SINAIS E SISTEMAS (GRÁFICOS)
    # ==============================================================================

    # Cores padronizadas para as classes
    cor_cab = '#800020' # Vinho Bordeaux (Cabernet)
    cor_syr = '#4B0082' # Índigo Escuro (Shiraz)

    # ---------------------------------------------------------
    # Gráfico 1: Barras Comparativas (Energia Média)
    # ---------------------------------------------------------
    ax = df_medias.T.plot(kind='bar', figsize=(10, 6), color=[cor_cab, cor_syr], edgecolor='black')
    plt.title('Assinatura Espectral Média: Cabernet vs Shiraz (SG)', fontsize=14, fontweight='bold')
    plt.ylabel('Energia Integrada da Banda (Absorbância $\\times$ cm$^{-1}$)', fontsize=12)
    plt.xlabel('Macronutrientes e Aromas', fontsize=12)
    plt.xticks(ticks=range(5), labels=['Açúcares', 'Ácidos Orgânicos', 'Polifenóis', 'Proteínas', 'Aromas (Ésteres)'], rotation=15)
    plt.legend(title='Classe da Uva', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def scatter_plot(df):

    cor_cab = '#800020' # Vinho Bordeaux (Cabernet)
    cor_syr = '#4B0082' # Índigo Escuro (Shiraz)
    # ---------------------------------------------------------
    # Gráfico 2: Espaço de Características (Scatter Plot)
    # Prova visual da separabilidade linear das classes
    # ---------------------------------------------------------
    plt.figure(figsize=(9, 6))

    cabernets = df[df['Uva'] == 'Cabernet']
    shiraz = df[df['Uva'] == 'Shiraz']

    plt.scatter(cabernets['area_polifenois'], cabernets['area_aroma'], 
                color=cor_cab, label='Cabernet', s=100, alpha=0.7, edgecolors='white', linewidth=1.5)

    plt.scatter(shiraz['area_polifenois'], shiraz['area_aroma'], 
                color=cor_syr, label='Shiraz', s=100, alpha=0.7, edgecolors='white', linewidth=1.5)

    plt.title('Espaço de Separação: Polifenóis vs Aromas', fontsize=14, fontweight='bold')
    plt.xlabel('Energia da Banda de Polifenóis (Taninos)', fontsize=12)
    plt.ylabel('Energia da Banda de Ésteres (Aromas)', fontsize=12)
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.show()

def plot_radar_chart(df_medias):

    cor_cab = '#800020' # Vinho Bordeaux (Cabernet)
    cor_syr = '#4B0082' # Índigo Escuro (Shiraz)

    # ---------------------------------------------------------
    # Gráfico 3: Gráfico de Radar (Perfil Químico Multidimensional)
    # ---------------------------------------------------------
    # Prepara os dados para o radar (precisa fechar o polígono repetindo o primeiro ponto)
    labels = ['Açúcares', 'Ácidos', 'Polifenóis', 'Proteínas', 'Aromas']
    num_vars = len(labels)
    angulos = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angulos += angulos[:1]  # Fecha o círculo

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Plota Cabernet
    valores_cab = df_medias.loc['Cabernet'].tolist()
    valores_cab += valores_cab[:1] # Fecha o polígono
    ax.plot(angulos, valores_cab, color=cor_cab, linewidth=2, label='Cabernet')
    ax.fill(angulos, valores_cab, color=cor_cab, alpha=0.25)

    # Plota Shiraz
    valores_syr = df_medias.loc['Shiraz'].tolist()
    valores_syr += valores_syr[:1] # Fecha o polígono
    ax.plot(angulos, valores_syr, color=cor_syr, linewidth=2, label='Shiraz')
    ax.fill(angulos, valores_syr, color=cor_syr, alpha=0.25)

    # Ajusta a estética do Radar
    ax.set_theta_offset(np.pi / 2) # Gira para o topo
    ax.set_theta_direction(-1) # Sentido horário
    ax.set_thetagrids(np.degrees(angulos[:-1]), labels, fontsize=11, fontweight='bold')

    plt.title('Identidade Espectral Multidimensional', y=1.08, fontsize=15, fontweight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    plt.tight_layout()
    plt.show()
