
import pandas as pd
import os
from scipy.signal import savgol_filter, find_peaks
import numpy as np

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
    Agrupa as colunas por vinho (ex: Wine_01) e calcula a média das triplicatas.
    Retorna um DataFrame onde cada coluna é um vinho único.
    """

    wine_tags = [col.rsplit('_', 1)[0] for col in df.columns]
    df_mean = df.groupby(wine_tags, axis=1).mean()
    return df_mean

def dsp_filter(serie_sinal, janela=11, ordem=2):
    """Aplica o filtro Savitzky-Golay em um sinal."""
    return savgol_filter(serie_sinal, window_length=janela, polyorder=ordem)

def extract_wine_metrics(serie_filtrada):
    """
    Identifica picos específicos e calcula a área sob a curva para
    Açúcar, Ácidos e Aromas (Ésteres).
    """
    # 1. Achar todos os picos do sinal
    indices_picos, _ = find_peaks(serie_filtrada, height=0.02)
    wavenumbers_picos = serie_filtrada.index[indices_picos]
    
    # Dicionário para guardar os resultados do vinho
    metrics = {
        'pico_açúcar': 0.0,
        'area_açúcar': 0.0,
        'pico_aroma': 0.0,
        'area_aroma': 0.0
    }

    # 2. Lógica para identificar e calcular áreas
    # Região Açúcar: 900 - 1150
    # Região Aroma (Ésteres): 1730 - 1750
    
    # Exemplo para Aroma:
    mask_aroma = (serie_filtrada.index >= 1730) & (serie_filtrada.index <= 1750)
    segmento_aroma = serie_filtrada[mask_aroma]
    if not segmento_aroma.empty:
        metrics['pico_aroma'] = segmento_aroma.max()
        # Regra do Trapézio para Integral (Concentração)
        metrics['area_aroma'] = np.trapz(segmento_aroma.values, x=segmento_aroma.index)
        
    # Exemplo para Açúcar:
    mask_açúcar = (serie_filtrada.index >= 900) & (serie_filtrada.index <= 1150)
    segmento_açúcar = serie_filtrada[mask_açúcar]
    if not segmento_açúcar.empty:
        metrics['pico_açúcar'] = segmento_açúcar.max()
        metrics['area_açúcar'] = np.trapz(segmento_açúcar.values, x=segmento_açúcar.index)

    return metrics