# Projeto: Processamento de Sinais em Espectros de Infravermelho (FTIR) de Vinhos

## 1. Introdução e Objetivo
Este projeto aplica conceitos da disciplina de **Análise de Sinais e Sistemas** para processar e interpretar dados reais de espectroscopia de infravermelho (FTIR) de vinhos tintos (Cabernet Sauvignon e Shiraz). 

O objetivo principal é utilizar técnicas de processamento digital de sinais (DSP) para limpar o ruído dos sensores, identificar picos de absorbância automaticamente e correlacionar esses picos com macronutrientes (proteínas e carboidratos) e compostos aromáticos (ésteres).

## 2. A Conexão com Sinais e Sistemas
Embora os dados venham da química de alimentos, a análise será fundamentada em ferramentas de engenharia:
* **Domínio da Frequência:** O eixo horizontal (Número de Onda em $cm^{-1}$) é tratado como uma frequência espacial.
* **Filtragem Digital:** Aplicação de filtros pass-baixa e suavização (Savitzky-Golay) para melhoria da Relação Sinal-Ruído (SNR).
* **Detecção de Transientes/Picos:** Uso de derivadas e algoritmos de busca de máximos locais para identificação de componentes químicos.
* **Análise de Amplitude:** Comparação da energia do sinal em frequências específicas para diferenciação de padrões.

## 3. Base de Dados
O conjunto de dados `Wine_FTIR_Triplicate_Spectra.csv` contém:
* **Amostras:** 37 garrafas de vinho analisadas em triplicata (111 espectros no total).
* **Variedades:** Cabernet Sauvignon e Shiraz.
* **Resolução:** 235 pontos de amostragem por espectro.
* **Faixa Espectral:** 899 a 1802 $cm^{-1}$ (Região da "Impressão Digital" molecular).

## 4. Metodologia Proposta (Etapas do Trabalho)

### Passo 1: Pré-processamento (Suavização)
Os espectros brutos podem conter ruídos espúrios. Utilizaremos o **Filtro de Savitzky-Golay** para suavizar o sinal, garantindo que a detecção de picos não seja afetada por oscilações de alta frequência.

### Passo 2: Identificação Automática de Componentes (Peak Picking)
Desenvolvimento de algoritmo para localizar picos significativos correlacionados à literatura de engenharia de alimentos:
* **Açúcares/Carboidratos:** Faixa de 900 - 1150 $cm^{-1}$.
* **Ácidos Orgânicos:** Próximo a 1200 $cm^{-1}$.
* **Proteínas (Amidas):** Região próxima a 1650 $cm^{-1}$.
* **Ésteres (Aromas):** Faixa de 1730 - 1750 $cm^{-1}$ (Estiramento $C=O$).

### Passo 3: Comparação de Assinaturas Espectrais
Análise comparativa entre as variedades (Cabernet vs. Shiraz) utilizando a média dos sinais e o desvio padrão das triplicatas para validar a precisão do sistema.

### Passo 4: Ranking de Intensidade Aromática
Cálculo da área sob a curva (integração do sinal) na região dos ésteres para classificar amostras com maior potencial de intensidade de aroma.

## 5. Requisitos de Software
* **Linguagem:** Python 3.x
* **Bibliotecas Principais:**
    * `pandas`: Manipulação de dados.
    * `scipy.signal`: Filtros digitais e detecção de picos.
    * `matplotlib`: Visualização de sinais.
    * `numpy`: Cálculos matemáticos de matrizes.
 
## Fonte dos Dados
Os dados utilizados neste projeto foram obtidos do repositório [Wine_Cabernet_Shiraz_FTIR](https://github.com/QIBChemometrics/Wine_Cabernet_Shiraz_FTIR) do Quadram Institute Bioscience.

**Referência Acadêmica:**
Kemsley EK, Defernez M, Marini, F (2019) *"Multivariate statistics: Considerations and confidences in food authenticity problems"*, Food Control, 105, 102-112.
