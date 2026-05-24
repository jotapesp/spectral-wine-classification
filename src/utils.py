
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

def extract_wine_metrics(serie_filtrada):
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
def compare_filters(df_mean, wine_column='Wine_01'):
    """
    Gera um gráfico comparando o sinal bruto, o filtro Savitzky-Golay
    e o filtro de Média Móvel (Convolução) para um vinho específico.
    """
    sinal_bruto = df_mean[wine_column]
    
    # Aplica os dois filtros
    sinal_savgol = dsp_filter(sinal_bruto, janela=11, ordem=2)
    sinal_convolucao = dsp_filter_moving_average(sinal_bruto, janela=7) # Janela 7 para visualização clara
    
    plt.figure(figsize=(12, 6))
    plt.plot(sinal_bruto.index, sinal_bruto.values, label='Sinal Bruto (Com Ruído)', alpha=0.4, color='gray')
    plt.plot(sinal_savgol.index, sinal_savgol.values, label='Filtro Savitzky-Golay (Ideal para Picos)', linewidth=2, color='blue')
    plt.plot(sinal_convolucao.index, sinal_convolucao.values, label='Média Móvel via Convolução (FIR)', linewidth=2, color='red', linestyle='--')
    
    plt.title(f'Comparação de Filtros SLIT-D - {wine_column}', fontsize=14)
    plt.xlabel('Wavenumbers ($cm^{-1}$)', fontsize=12)
    plt.ylabel('Absorbância', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()