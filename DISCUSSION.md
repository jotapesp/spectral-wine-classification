
### 1. Embasamento Teórico e Modelagem dos Dados
Na disciplina, estamos acostumados com sinais variando no tempo ($t$) ou em amostras temporais discretas ($n$). No projeto, a variável independente não é o tempo, mas sim o **número de onda (wavenumber)**.
*   **O Sinal:** O espectro é um **sinal de tempo discreto $x[n]$** de duração finita, onde $n$ varia de $0$ a $234$ (representando os 235 pontos na faixa de $899$ a $1802 \text{ cm}^{-1}$), e a amplitude $x[n]$ é a absorbância medida em cada ponto. 
*   **O Sistema:** O código Python atua como um **Sistema Linear Invariante no Tempo Discreto (SLIT-D)**. A entrada é o espectro com ruído $x[n]$ e a saída é o espectro processado $y[n]$.

---

### 2. Traduzindo a Metodologia (Passo a Passo)

**Passo 1: Pré-processamento (Média e Suavização)**
*   **Média de Conjunto:** A operação de calcular a média das triplicatas baseia-se na **propriedade da aditividade e homogeneidade (superposição)** dos sistemas lineares. Ao somar os sinais e dividir por 3, cancelam-se componentes aleatórios (ruído de média zero) reforçando o sinal determinístico.
*   **Suavização (Filtragem):** O ruído dos sensores se manifesta como flutuações rápidas de amostra para amostra, o que, na teoria, corresponde a **componentes de alta frequência**. Portanto, a suavização é a aplicação de um **filtro passa-baixas**, que atenua essas altas frequências e permite a passagem das variações lentas (os picos químicos reais). O Savitzky-Golay é, na prática, um filtro digital do tipo **FIR (Resposta ao Impulso Finita - não recursivo)**.

**Passo 2: Identificação Automática de Componentes (Peak Picking)**
*   Para encontrar picos automaticamente, costuma-se buscar os pontos onde a inclinação da curva muda de positiva para negativa. Em Sinais e Sistemas, essa operação de calcular a inclinação (derivada) no domínio discreto é implementada pelo sistema de **Primeira Diferença**: $y[n] = x[n] - x[n-1]$. O filtro diferenciador é um sistema de natureza **passa-altas**, que amplifica mudanças bruscas e bordas, ajudando a isolar a posição exata dos picos na "Região da Impressão Digital".

**Passo 3: Comparação de Assinaturas Espectrais**
*   A "análise de variância" ou comparação de amplitude de uma banda específica ($1400 - 1600 \text{ cm}^{-1}$) pode ser justificada matematicamente pelo cálculo de **Energia do Sinal** num dado intervalo discreto: $E = \sum_{n=N_1}^{N_2} |x[n]|^2$. 

**Passo 4: Ranking de Intensidade Aromática**
*   O "cálculo da área sob a curva" é a operação inversa da diferença. Em sistemas discretos, a integração é realizada por um **Acumulador**, que é um sistema SLIT-D cuja resposta ao impulso é o degrau unitário ($h[n] = u[n]$), resultando na soma de convolução $y[n] = \sum_{k=-\infty}^{n} x[k]$.

---

### 3. Desenvolvendo Filtro Próprio (Alternativa ao Savitzky-Golay)
A ideia é modelar e implementar o clássico **Filtro de Média Móvel (Moving Average Filter)**. Ele é o exemplo fundamental de filtro FIR passa-baixas ensinado nos livros textos.

**A Matemática (Para o relatório):**
A equação de diferenças de um filtro de média móvel não recursivo que usa $M$ pontos passados, o ponto atual e $M$ pontos futuros (janela simétrica de tamanho $2M+1$) é dada por:
$$y[n] = \frac{1}{2M+1} \sum_{k=-M}^{M} x[n-k]$$

A **resposta ao impulso** $h[n]$ deste sistema é simplesmente um pulso retangular:
$$h[n] = \begin{cases} \frac{1}{2M+1}, & \text{para } -M \le n \le M \\ 0, & \text{caso contrário} \end{cases}$$

Fazer essa filtragem no código Python equivale a aplicar a **Soma de Convolução** entre o sinal $x[n]$ e a resposta ao impulso $h[n]$:
$$y[n] = x[n] * h[n]$$

**Como implementar no Python para comparar:**
No código, a função `dsp_filter_moving_average` é responsável por essa implementação. Ela cria a resposta ao impulso `h` e usar a função nativa de convolução do *NumPy* (`np.convolve`).

```python
import numpy as np
import matplotlib.pyplot as plt

# Suponha que 'x' seja um array do numpy com os 235 pontos de absorbância do vinho
# x = espectro_vinho_com_ruido

# Definindo o tamanho da janela do filtro (equivalente a 2M + 1)
# Exemplo: Janela de 5 pontos (M = 2)
tamanho_janela = 5

# 1. Construindo a resposta ao impulso h[n] do Filtro de Média Móvel
h_n = np.ones(tamanho_janela) / tamanho_janela 

# 2. Aplicando o sistema SLIT-D através da Convolução Discreta
y_media_movel = np.convolve(x, h_n, mode='same')

# (Você usará o mode='same' para que o tamanho de saída continue 235 pontos)
```

### No fim das contas...
Apresentar um gráfico com 3 curvas sobrepostas:
1. O sinal original com ruído ($x[n]$).
2. O sinal filtrado pela "caixa-preta" da biblioteca (`scipy.signal.savgol_filter`).
3. O sinal filtrado pelo seu **Filtro de Média Móvel implementado via Convolução Discreta** ($x[n] * h[n]$).

**Discussão:** O Filtro de Média Móvel é o filtro passa-baixas mais cru. Ele suaviza o ruído excelentemente, mas em contrapartida, pelo compromisso tempo-frequência, ele "alarga" ou "achata" os picos dos macronutrientes do vinho se a janela for muito grande. Já o filtro de Savitzky-Golay (que ajusta polinômios locais em vez de uma média plana) é um filtro FIR mais sofisticado projetado exatamente para preservar a altura/resolução dos picos.