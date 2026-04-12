
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
    
    # Aroma (Ésteres):
    mask_aroma = (serie_filtrada.index >= 1730) & (serie_filtrada.index <= 1750)
    segmento_aroma = serie_filtrada[mask_aroma]
    if not segmento_aroma.empty:
        metrics['pico_aroma'] = segmento_aroma.max()
        # Regra do Trapézio para Integral (Concentração)
        metrics['area_aroma'] = np.trapz(segmento_aroma.values, x=segmento_aroma.index)
        
    # Açúcar:
    mask_acucar = (serie_filtrada.index >= 900) & (serie_filtrada.index <= 1150)
    segmento_acucar = serie_filtrada[mask_acucar]
    if not segmento_acucar.empty:
        metrics['pico_acucar'] = segmento_acucar.max()
        metrics['area_acucar'] = np.trapz(segmento_acucar.values, x=segmento_acucar.index)
    
    # Polifenois:
    mask_polifenois = (serie_filtrada.index >= 1400) & (serie_filtrada.index <= 1600)
    segmento_polifenois = serie_filtrada[mask_polifenois]
    if not segmento_polifenois.empty:
        metrics['pico_polifenois'] = segmento_polifenois.max()
        metrics['area_polifenois'] = np.trapz(segmento_polifenois.values, x=segmento_polifenois.index)
    
    # Proteínas:
    mask_proteinas = (serie_filtrada.index >= 1600) & (serie_filtrada.index <= 1700)
    segmento_proteinas = serie_filtrada[mask_proteinas]
    if not segmento_proteinas.empty:
        metrics['pico_proteinas'] = segmento_proteinas.max()
        metrics['area_proteinas'] = np.trapz(segmento_proteinas.values, x=segmento_proteinas.index)
    
    # Ácidos Organicos (1200 cm-1): 
    mask_acidos = (serie_filtrada.index >= 1160) & (serie_filtrada.index <= 1240)
    segmento_acidos = serie_filtrada[mask_acidos]
    if not segmento_polifenois.empty:
        metrics['pico_acidos'] = segmento_acidos.max()
        metrics['area_acidos'] = np.trapz(segmento_acidos.values, x=segmento_acidos.index)

    return metrics