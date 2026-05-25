import utils
import pandas as pd
import matplotlib.pyplot as plt

def main():
    print("=== Iniciando o Processamento de Sinais de Vinho (FTIR) ===")

    # 1. Carregar os dados espectrais do ficheiro CSV
    print("\n[1/4] A carregar dados...")
    df = utils.load_data(utils.file_path)

    # 2. Aplicar o Princípio da Superposição para limpar o ruído aleatório das triplicatas
    print("[2/4] A calcular a média das triplicatas (Cancelamento de Ruído)...")
    df_mean = utils.calc_mean(df)
    print(f"Total de vinhos únicos identificados: {len(df_mean.columns)}")

    # 3. Loop para processar coluna por coluna (vinho por vinho)
    print("[3/4] A aplicar filtros digitais e a extrair métricas...")
    resultados_sg = []
    resultados_ma = []

    for coluna in df_mean.columns:
        # A. Aplicar os sistemas de filtragem digitais
        sinal_limpo_sg = utils.dsp_filter(df_mean[coluna])                  # Savitzky-Golay
        sinal_limpo_ma = utils.dsp_filter_moving_average(df_mean[coluna])   # Média Móvel (Convolução)

        # B. Extrair as métricas espectrais importantes
        metrics_sg = utils.extract_wine_metrics(sinal_limpo_sg)
        metrics_ma = utils.extract_wine_metrics(sinal_limpo_ma)
        
        # C. Adicionar a etiqueta do nome do vinho para não perder a referência
        metrics_sg['Vinho'] = coluna
        metrics_ma['Vinho'] = coluna
        
        # D. Guardar nas respetivas listas globais
        resultados_sg.append(metrics_sg)
        resultados_ma.append(metrics_ma)

    # 4. Converter resultados para DataFrames e mostrar no terminal
    print("[4/4] Processamento concluído! Resultados obtidos:")
    
    df_resultados_sg = pd.DataFrame(resultados_sg).set_index('Vinho')
    df_resultados_ma = pd.DataFrame(resultados_ma).set_index('Vinho')

    print("\n--- METRICAS EXTRAIDAS COM FILTRO SAVITZKY-GOLAY (Primeiras Linhas) ---")
    print(df_resultados_sg.head())
    df_resultados_sg.to_csv('../results/savitzky_golay_corrigido.csv', index=False)

    print("\n--- METRICAS EXTRAIDAS COM FILTRO DE MEDIA MOVEL (Primeiras Linhas) ---")
    print(df_resultados_ma.head())
    df_resultados_ma.to_csv('../results/media_movel_corrigido.csv', index=False)

    # 5. Gerar e exibir os gráficos comparativos
    print("\n[Gráficos] A gerar visualizações comparativas de filtros...")
    utils.compare_filters(df, df_mean, wine_column='Wine_01_Cab')
    utils.compare_filters(df, df_mean, wine_column='Wine_15_Syr')
    utils.compare_filters(df, df_mean, wine_column='Wine_30_Cab')

    utils.highlight_triple_avg(df, df_mean, wine_column='Wine_01_Cab')
    utils.highlight_triple_avg(df, df_mean, wine_column='Wine_15_Syr')
    utils.highlight_triple_avg(df, df_mean, wine_column='Wine_30_Cab')

    print("Abrirndo a janela de gráficos. Fecha a janela para encerrar o programa.")
    plt.show() # IMPORTANTE: No VSCode, esta linha trava a execução e segura a janela do gráfico aberta.

if __name__ == "__main__":
    main()