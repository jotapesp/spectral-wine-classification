# RELATÓRIO TÉCNICO-CIENTÍFICO: PROCESSAMENTO DIGITAL DE SINAIS ESPECTRAIS (FTIR)
**Abordagem Computacional sob a Ótica de Sistemas Lineares e Invariantes no Tempo (SLIT-D)** **Fundamentação Teórica:** Alan V. Oppenheim & Alan S. Willsky (*Sinais e Sistemas*, 2ª Ed.) e Material Didático Institucional (Aulas 01 a 14)

---

## 1. MODELAGEM ESPACIAL DO SINAL E DO SISTEMA

Na análise clássica de Processamento Digital de Sinais (PDS), a variável independente costuma representar o tempo discreto ($n$ ou $k$). Contudo, a modelagem matemática de Sistemas Lineares e Invariantes no Tempo Discretos (SLIT-D) é perfeitamente isomórfica e aplicável a domínios onde a variável independente é uma coordenada espacial ou física. No presente projeto, o sinal bruto é proveniente de um espectrômetro de Infravermelho por Transformada de Fourier (FTIR).

### Mapeamento Matemático do Sinal
* **Variável Independente ($n$):** Representa o número de onda discreto ($\text{wavenumber}$, medido em $\text{cm}^{-1}$). O arquivo de dados é composto por $N = 235$ amostras uniformemente distribuídas no intervalo físico de $899.215 \text{ cm}^{-1}$ a $1802.564 \text{ cm}^{-1}$. O índice discreto $n \in \mathbb{Z}$ mapeia linearmente cada ponto amostrado:
  $$n = 0, 1, 2, \dots, N-1 \quad (N=235)$$
* **Amplitude do Sinal ($x[n]$):** Corresponde à intensidade de absorbância óptica medida no número de onda associado ao índice $n$. O sinal de entrada de qualquer canal (vinho) pode ser modelado como:
  $$x[n] = v[n] + e[n]$$
  Onde $v[n]$ é o componente determinístico e verdadeiro do sinal (absorbância real dos compostos químicos do vinho) e $e[n]$ representa o ruído estocástico de alta frequência induzido por flutuações térmicas e eletrônicas do sensor da máquina.

### Caracterização Geral do Sistema
O processamento digital do sinal espectral é composto por uma cascata de sistemas discretos. Cada estágio recebe uma sequência de entrada e entrega uma sequência de saída transformada, atuando diretamente sobre o vetor amostral para otimizar a Relação Sinal-Ruído (SNR) e isolar as componentes harmônicas correlacionadas aos macronutrientes químicos.

---

## 2. ESTÁGIO I: FILTRAGEM POR MÉDIA DE CONJUNTO (TRIPLICATAS) E O PRINCÍPIO DA SUPERPOSIÇÃO

O primeiro sistema da cascata realiza o pré-processamento estatístico das leituras efetuadas em triplicata para uma mesma amostra biológica. 

### Conexão Teórica: Propriedades do Sistema (Aula 01)
Um sistema $T\{\cdot\}$ é classificado como **Linear** se cumpre simultaneamente os princípios de **Aditividade** e **Homogeneidade** (Teorema da Superposição de Oppenheim). Se:
$$T\{x_1[n]\} = y_1[n] \quad \text{e} \quad T\{x_2[n]\} = y_2[n]$$
Então, para quaisquer escalares $a, b \in \mathbb{C}$:
$$T\{a \cdot x_1[n] + b \cdot x_2[n]\} = a \cdot y_1[n] + b \cdot y_2[n]$$

O algoritmo implementado na função `calc_mean` baseia-se diretamente nessa propriedade linear. Sejam $x_{\text{Rep1}}[n]$, $x_{\text{Rep2}}[n]$ e $x_{\text{Rep3}}[n]$ as três entradas discretas coletadas de forma independente. O sistema de média realiza a seguinte combinação linear:
$$y_{\text{mean}}[n] = \frac{1}{3}x_{\text{Rep1}}[n] + \frac{1}{3}x_{\text{Rep2}}[n] + \frac{1}{3}x_{\text{Rep3}}[n]$$

### Mecanismo de Cancelamento do Ruído Estocástico
Ao expandirmos cada réplica em seu componente determinístico (sinal verdadeiro invariante $v[n]$) e seu componente aleatório (ruído $e_i[n]$), temos:
$$x_{\text{Rep1}}[n] = v[n] + e_1[n]$$
$$x_{\text{Rep2}}[n] = v[n] + e_2[n]$$
$$x_{\text{Rep3}}[n] = v[n] + e_3[n]$$

Aplicando o princípio da superposição linear do sistema:
$$y_{\text{mean}}[n] = \frac{1}{3}\Big( (v[n] + e_1[n]) + (v[n] + e_2[n]) + (v[n] + e_3[n]) \Big)$$
$$y_{\text{mean}}[n] = v[n] + \frac{e_1[n] + e_2[n] + e_3[n]}{3}$$

Assumindo que o ruído do sensor é um processo ergódico de **média zero** ($E\{e[n]\} = 0$) e não correlacionado entre as medições, a soma estatística dos ruídos independentes decai em direção à sua esperança matemática (zero). Por outro lado, as amplitudes do sinal determinístico $v[n]$, por estarem em fase e apresentarem perfeita coerência espacial, reforçam-se mutuamente. O sistema atua eliminando a variabilidade inter-amostral (*ruído de deslocamento amostral*), entregando um sinal com patamar de ruído atenuado para o próximo estágio.

---

## 3. ESTÁGIO II: SUAVIZAÇÃO ESPACIAL E FILTROS PASSA-BAIXAS DISCRETOS

Após a consolidação das triplicatas, o sinal limpo de patamar $y_{\text{mean}}[n]$ entra no segundo bloco do sistema, focado em eliminar o ruído intra-amostral de alta frequência (transientes rápidos de flutuação ponto a ponto). Duas abordagens de filtragem digital baseadas em janelas móveis são avaliadas.

---

### ABORDAGEM A: Filtro de Média Móvel Convencional

O Filtro de Média Móvel é implementado via **Soma de Convolução Discreta**, caracterizando um sistema cuja saída atual é a média aritmética simples de um número finito de amostras vizinhas da entrada.



#### Resposta ao Impulso $h_{\text{ma}}[n]$
A resposta ao impulso unitário de um sistema LIT determina completamente o seu comportamento no domínio discreto. Para uma janela causal de tamanho $M$ (onde o parâmetro de código `janela=5`), a resposta ao impulso $h_{\text{ma}}[n]$ é uma função pulso retangular discretizada e normalizada:
$$h_{\text{ma}}[n] = \frac{1}{M} \Big( u[n] - u[n-M] \Big) = \begin{cases} \frac{1}{M}, & 0 \le n \le M-1 \\ 0, & \text{caso contrário} \end{cases}$$

#### Equação de Diferenças Lineares com Coeficientes Constantes
A relação entrada-saída no domínio do tempo/espaço discreto é expressa por:
$$y[n] = \frac{1}{M} \sum_{k=0}^{M-1} x[n-k] = \frac{1}{M}x[n] + \frac{1}{M}x[n-1] + \dots + \frac{1}{M}x[n-(M-1)]$$

#### Análise no Domínio Z e Função de Transferência $H_{\text{ma}}(z)$
Aplicando a propriedade da linearidade e do deslocamento temporal da Transformada Z (Aula 12 e Aula 14):
$$\mathcal{Z}\{x[n-k]\} = X(z) \cdot z^{-k}$$
A transformação da equação de diferenças resulta em:
$$Y(z) = \frac{1}{M} \left( 1 + z^{-1} + z^{-2} + \dots + z^{-(M-1)} \right) X(z)$$
Portanto, a Função de Transferência do sistema é dada pela série geométrica finita:
$$H_{\text{ma}}(z) = \frac{Y(z)}{X(z)} = \frac{1}{M} \sum_{k=0}^{M-1} z^{-k} = \frac{1}{M} \left( \frac{1 - z^{-M}}{1 - z^{-1}} \right) = \frac{1}{M} \left( \frac{z^M - 1}{z^{M-1}(z - 1)} \right)$$

#### Mapeamento de Polos, Zeros e Região de Convergência (ROC)
* **Polos:** O denominador da função de sistema possui raízes em $z^{M-1} = 0$, o que indica um polo múltiplo de ordem $(M-1)$ localizado exatamente na **origem** do plano complexo Z ($z = 0$). O termo $(z - 1)$ no denominador sugere um polo em $z = 1$, porém ele é cancelado exatamente por um zero idêntico vindo do numerador.
* **Zeros:** As raízes do numerador são dadas por $z^M = 1$, correspondendo às **raízes complexas da unidade**. Elas estão uniformemente distribuídas sobre o círculo unitário nas frequências angulares discretas $\Omega_k = \frac{2\pi k}{M}$, para $k = 1, 2, \dots, M-1$ (excluindo $k=0$ devido ao cancelamento do polo em $1$).
* **Região de Convergência (ROC):** Como o sistema possui uma resposta ao impulso de duração finita (filtro FIR), a ROC não é limitada por polos intermediários. A convergência é garantida em todo o plano complexo Z, exceto na origem, devido às potências negativas de $z$. Logo:
  $$\text{ROC: } 0 < |z| < \infty$$

#### Classificação Teórica Completa do Sistema
1. **FIR vs. IIR:** Classificado estritamente como um filtro **FIR (Finite Impulse Response)**. A resposta ao impulso possui suporte compacto e duração estritamente finita ($M$ amostras).
2. **Causalidade:** Na sua formulação matemática padrão via Transformada Z, o sistema é **Causal**, pois $h_{\text{ma}}[n] = 0$ para $n < 0$. Contudo, na implementação prática do algoritmo via Python (utilizando o parâmetro `mode='same'`), o centro da janela é alinhado simetricamente ao ponto presente. Isso converte a operação real em um sistema **Não-Causal (Bilateral)** que necessita de pontos futuros para o cálculo do ponto corrente.
3. **Estabilidade BIBO:** Um sistema discreto é estável no sentido Bounded-Input Bounded-Output (BIBO) se sua resposta ao impulso for absolutamente somável (Aula 04):
   $$\sum_{n=-\infty}^{\infty} |h_{\text{ma}}[n]| = \sum_{n=0}^{M-1} \left| \frac{1}{M} \right| = M \cdot \frac{1}{M} = 1 < \infty$$
   Como a soma converge para um valor finito (e, equivalentemente, a ROC engloba perfeitamente o círculo unitário $|z|=1$), o filtro é **Inerentemente Estável**.
4. **Memória:** Sistema **Com Memória**. A saída $y[n]$ necessita do armazenamento de estados passados da entrada.
5. **Resposta em Frequência (Filtro Passa-Baixas):** Ao avaliarmos $H_{\text{ma}}(z)$ sobre o círculo unitário ($z = e^{j\Omega}$), obtemos a função que descreve o comportamento senoidal estável (Aula 07 / Aula 10):
   $$H_{\text{ma}}(e^{j\Omega}) = \frac{1}{M} \frac{\sin\left(\frac{\Omega M}{2}\right)}{\sin\left(\frac{\Omega}{2}\right)} e^{-j\frac{\Omega(M-1)}{2}}$$
   Essa resposta em frequência possui o formato de uma função *Sinc discretizada* (ou núcleo de Dirichlet). Ela exibe ganho unitário na frequência zero ($\Omega = 0$) e atenua progressivamente as componentes de frequência angular mais elevada (variações bruscas ponto a ponto no gráfico espectral), atuando formalmente como um **Filtro Passa-Baixas**.

---

### ABORDAGEM B: Filtro de Suavização de Savitzky-Golay

O Filtro de Savitzky-Golay representa uma evolução matemática em relação à média móvel convencional para processamento de dados químicos e espectrais. O sistema opera aproximando localmente subconjuntos contíguos de dados por um polinômio de baixa ordem através do método analítico dos mínimos quadrados.

#### Princípio Teórico do Sistema
Diferente da média simples, que assume um comportamento plano dentro da janela móvel, o filtro Savitzky-Golay assume que o sinal verdadeiro local pode ser modelado por uma curva polinomial de grau $P$ (no código, adotou-se um polinômio quadrático, `ordem=2`):
$$p(m) = a_0 + a_1 m + a_2 m^2$$
Para cada janela contendo $M = 2L + 1$ pontos (onde `janela=11`, implicando em $L=5$ vizinhos para cada lado), o algoritmo minimiza o erro quadrático residual entre os pontos reais do espectro e o polinômio estimado. O valor final suavizado da saída $y[n]$ corresponde exatamente ao valor do polinômio avaliado em seu ponto central ($m=0$), o que implica matematicamente que $y[n] = a_0$.

#### Formulação Algébrica como Sistema FIR Não-Causal
Embora deduzido via regressão estatística linear, a maior contribuição teórica de Savitzky e Golay foi demonstrar que o ajuste polinomial contínuo ponto a ponto equivale estritamente a uma **Soma de Convolução Discreta com Coeficientes Fixos**. O sistema resolve internamente as matrizes de projeção ortogonal dos mínimos quadrados e extrai um vetor imutável de coeficientes simétricos de filtragem ($h_{\text{sg}}[m]$).

A equação de diferenças linear do filtro de Savitzky-Golay expressa a saída corrente como uma combinação linear bilateral simétrica das amostras de entrada:
$$y[n] = \sum_{m=-L}^{L} h_{\text{sg}}[m] \cdot x[n-m]$$
Substituindo o parâmetro do projeto ($L=5$, oriundo de uma janela de 11 pontos):
$$y[n] = h_{\text{sg}}[-5]x[n+5] + h_{\text{sg}}[-4]x[n+4] + \dots + h_{\text{sg}}[0]x[n] + \dots + h_{\text{sg}}[5]x[n-5]$$

#### Função de Transferência $H_{\text{sg}}(z)$ e Região de Convergência (ROC)
Aplicando a propriedade do deslocamento temporal da Transformada Z bilateral para obter a função de sistema no domínio complexo:
$$H_{\text{sg}}(z) = \sum_{m=-5}^{5} h_{\text{sg}}[m] \cdot z^{-m} = h_{\text{sg}}[-5]z^{5} + h_{\text{sg}}[-4]z^{4} + \dots + h_{\text{sg}}[0] + \dots + h_{\text{sg}}[5]z^{-5}$$



* **Polos e Zeros:** Por tratar-se de um polinômio complexo de potências tanto positivas quanto negativas de $z$, o sistema possui polos concentrados unicamente na origem ($z=0$, devido aos termos de tempo passado $z^{-m}$) e polos no infinito ($z=\infty$, devido aos termos de tempo futuro $z^{m}$). Não há polos no plano intermediário.
* **ROC (Região de Convergência):** Por ser uma sequência bilateral de duração estritamente finita (11 pontos), a ROC converge absolutamente em todas as regiões do plano Z, exceto nas suas descontinuidades extremas de fronteira:
  $$\text{ROC: } 0 < |z| < \infty$$

#### Classificação Teórica do Filtro de Savitzky-Golay
1. **Finito (FIR):** Sistema **FIR**. A resposta ao impulso decai e zera de forma absoluta fora do intervalo determinado pelo tamanho da janela móvel.
2. **Não-Causal / Bilateral:** O sistema é inerentemente **Não-Causal**. A determinação da saída suavizada no ponto presente $n$ exige o conhecimento das 5 amostras futuras da entrada ($x[n+1]$ até $x[n+5]$). Sua existência e computabilidade são viabilizadas pelo fato de os dados espectrais do arquivo estarem completamente amostrados e estáticos em memória, permitindo que a janela computacional acesse as posições futuras indexadas no DataFrame.
3. **Estabilidade Estrita:** Como todos os coeficientes $h_{\text{sg}}[m]$ são finitos e a janela possui tamanho limitado, a soma absoluta dos impulsos converge para um teto numérico constante. O círculo unitário $|z|=1$ está integralmente contido na ROC. O sistema é **Estritamente Estável** e livre de oscilações divergentes ou transientes exponenciais descontrolados.
4. **Preservação de Momentos de Alta Frequência (Vantagem sobre a Média Móvel):** Enquanto a média móvel atua achatando picos reais ao realizar a média simples de transições agudas, a resposta em frequência de Savitzky-Golay é projetada para manter inalterados os momentos estatísticos de ordem superior do sinal. Ela funciona como um filtro passa-baixas com banda de passagem mais plana, preservando com precisão a amplitude máxima (altura do pico) e a largura das bandas de absorbância química do vinho.

---

## 4. ESTÁGIO III: FILTROS PASSA-BANDA IDEAIS VIA FUNÇÕES SINGULARES (DEGRAU UNITÁRIO DESLOCADO)

Uma vez que o sinal médio espectral foi devidamente limpo e suavizado pelos filtros passa-baixas de segundo estágio, o sistema avança para a etapa de segmentação química. O objetivo deste bloco é isolar faixas de interesse do número de onda associadas a macronutrientes específicos.

### Modelagem Matemática via Funções Singulares Discretas (Aula 02 / Aula 14)
Na teoria clássica de sinais, a função **Degrau Unitário Discreto** ($\tilde{1}[n]$ ou $u[n]$) é a função singular fundamental de acumulação, definida por:
$$\tilde{1}[n] = \begin{cases} 1, & n \ge 0 \\ 0, & n < 0 \end{cases}$$

Para isolar uma janela retangular contígua de dados espectrais que se estenda do número de onda inicial indexado como $n_{\text{inicial}}$ até o número de onda final indexado como $n_{\text{final}}$, o sistema constrói matematicamente uma função de corte $w[n]$ baseada na subtração de duas funções degrau unitário devidamente deslocadas no espaço discreto:
$$w[n] = \tilde{1}[n - n_{\text{inicial}}] - \tilde{1}[n - (n_{\text{final}} + 1)]$$



Multiplicar o sinal suavizado $y[n]$ por essa função janela $w[n]$ equivale à aplicação de uma máscara booleana ideal:
$$y_{\text{isolado}}[n] = y[n] \cdot w[n] = y[n] \cdot \Big( \tilde{1}[n - n_{\text{inicial}}] - \tilde{1}[n - (n_{\text{final}} + 1)] \Big)$$

### Aplicação Prática dos Intervalos Passa-Banda
Essa operação matemática limpa e zera todas as regiões adjacentes do espectro, permitindo passagem linear exclusiva para os números de onda de interesse mapeados no projeto:
* **Filtro Passa-Banda I (Açúcares/Carboidratos):** $n$ correspondente à faixa de $900 \text{ a } 1150 \text{ cm}^{-1}$.
* **Filtro Passa-Banda II (Ácidos Orgânicos):** $n$ correspondente à região próxima a $1200 \text{ cm}^{-1}$ ($1160 - 1240 \text{ cm}^{-1}$).
* **Filtro Passa-Banda III (Polifenóis/Taninos):** $n$ correspondente ao intervalo de $1400 \text{ a } 1600 \text{ cm}^{-1}$.
* **Filtro Passa-Banda IV (Proteínas/Amidas):** $n$ correspondente ao intervalo de $1600 \text{ a } 1700 \text{ cm}^{-1}$.
* **Filtro Passa-Banda V (Ésteres/Aromas):** $n$ correspondente à faixa estreita de $1730 \text{ a } 1750 \text{ cm}^{-1}$.

Analisado sob a perspectiva do domínio de frequências espaciais, esse fatiamento geométrico atua como um conjunto de **Filtros Passa-Banda Ideais**.

---

## 5. ESTÁGIO IV: SISTEMA ACUMULADOR DISCRETO E QUANTIFICAÇÃO DE ENERGIA (MÉTRICAS ESPECTRAIS)

O último estágio evolutivo do sinal processado consiste na extração de parâmetros numéricos para subsidiar a classificação dos vinhos. O algoritmo executa o cálculo de duas métricas fundamentais sobre o sinal isolado de banda passante $y_{\text{isolado}}[n]$.

### A Métrica de Pico via Topologia Local e Proeminência
A busca simples por valores máximos absolutos ($y_{\max} = \max(y_{\text{isolado}})$) introduz erros sistemáticos causados por flutuações e elevações verticais da linha de base do sinal (desvios DC de frequência zero). 

A função atualizada do projeto contorna essa limitação aplicando o algoritmo de **Proeminência Espectral** (`find_peaks`). O sistema avalia as derivadas de primeira e segunda ordem discretas para mapear a topologia local do sinal. 



A proeminência calcula a altura líquida vertical entre o topo de uma oscilação harmônica e o vale mais profundo adjacente a ela. Isso remove matematicamente o ganho DC indesejado e garante que o pico extraído reflita com fidelidade a verdadeira amplitude de vibração das ligações moleculares da substância, mapeando o pico dinâmico em vez da quina geométrica induzida pelo corte da janela retangular.

### A Métrica de Área via Sistema Acumulador Discreto
O cálculo da área integrada sob o gráfico espectral é modelado na teoria de PDS como a aplicação de um **Sistema Acumulador Discreto**. Conforme documentado na Aula 14, um acumulador digital (ou integrador discreto aproximado) possui a seguinte equação de diferenças:
$$s[n] = s[n-1] + T_s \cdot y_{\text{isolado}}[n]$$
Onde $T_s$ representa o intervalo de amostragem entre pontos consecutivos. A função `np.trapezoid` do projeto estende esse conceito linear implementando a integração numérica trapezoidal fechada, cuja equação de diferenças acumulativa pondera os trapézios discretos espaciais:
$$s[n] = s[n-1] + \frac{\Delta \nu}{2} \Big( y_{\text{isolado}}[n] + y_{\text{isolado}}[n-1] \Big)$$

### A Conexão com a Física do Problema: Lei de Beer-Lambert
A integração discreta do sinal entrega a energia espectral total contida na banda de passagem da substância química. De acordo com a **Lei de Beer-Lambert**, a absorbância medida $A$ é linearmente proporcional à concentração do analito na solução:
$$A = \varepsilon \cdot b \cdot c$$
Onde $\varepsilon$ é a absortividade molar, $b$ é o caminho óptico interno da célula e $c$ é a concentração molar. Como os parâmetros físicos e de infraestrutura do sensor são constantes nas medições, a integração realizada pelo sistema acumulador discreto extrai uma métrica estatisticamente estável que quantifica a **Concentração Relativa** do macronutriente ou composto aromático presente em cada variedade de vinho estudada.

---

## 6. ABORDAGEM MATRICIAL, CONVOLUÇÃO CIRCULAR E A TRANSFORMADA DE FOURIER DISCRETA (DFT)

Um dos pilares estruturais da ementa de Sinais e Sistemas é a equivalência entre a convolução no domínio do tempo/espaço e a multiplicação linear no domínio da frequência (Teorema da Convolução de Oppenheim). O projeto avalia duas formas de execução matemática para a filtragem passa-baixas.

---

### ABORDAGEM 1: Processamento Algébrico no Domínio do Espaço Discreto via Matriz Circulante

A operação de convolução linear realizada pelo filtro de média móvel pode ser inteiramente mapeada e executada como uma operação pura de álgebra linear (multiplicação matricial). Para sinais de duração finita, construímos uma **Matriz Circulante** baseada nos coeficientes deslocados da resposta ao impulso $h[n]$.

Se modelarmos um sinal espectral reduzido de 4 pontos $x = [x_0, x_1, x_2, x_3]^T$ passando por um sistema de média móvel de 3 pontos com resposta $h = [\frac{1}{3}, \frac{1}{3}, \frac{1}{3}, 0]^T$, a operação linear de filtragem circular no espaço discreto adquire a seguinte forma de produto matricial:
$$y = H_{\text{circ}} \cdot x \implies \begin{bmatrix} y_0 \\ y_1 \\ y_2 \\ y_3 \end{bmatrix} = \begin{bmatrix} h_0 & h_3 & h_2 & h_1 \\ h_1 & h_0 & h_3 & h_2 \\ h_2 & h_1 & h_0 & h_3 \\ h_3 & h_2 & h_1 & h_0 \end{bmatrix} \begin{bmatrix} x_0 \\ x_1 \\ x_2 \\ x_3 \end{bmatrix} = \begin{bmatrix} \frac{1}{3} & 0 & \frac{1}{3} & \frac{1}{3} \\ \frac{1}{3} & \frac{1}{3} & 0 & \frac{1}{3} \\ \frac{1}{3} & \frac{1}{3} & \frac{1}{3} & 0 \\ 0 & \frac{1}{3} & \frac{1}{3} & \frac{1}{3} \end{bmatrix} \begin{bmatrix} x_0 \\ x_1 \\ x_2 \\ x_3 \end{bmatrix}$$

Cada linha da matriz circulante executa de forma mecânica e estática o deslocamento e a acumulação da convolução. Contudo, a multiplicação direta por matrizes circulantes gera inerentemente uma **Convolução Circular** (onde as extremidades do sinal dão a volta e se misturam). 

Para forçar que uma estrutura matricial circular entregue o resultado exato de uma **Convolução Linear** (necessária para manter a fidelidade física do espectro do vinho), é obrigatório aplicar a técnica de **Enchimento de Zeros (Zero Padding)**. Ambos os vetores de sinal e filtro com comprimentos originais $N$ e $M$ devem ser estendidos com zeros até atingirem o tamanho mínimo de suporte linear:
$$N_{\text{total}} = N + M - 1$$
Somente após esse preenchimento, a rotação dos elementos da matriz circulante processa o esvaziamento correto da memória do filtro, garantindo a perfeita equivalência matemática entre os domínios.

---

### ABORDAGEM 2: Processamento Harmônico no Domínio da Frequência via Transformada de Fourier Discreta (DFT)

A segunda rota de processamento migra os dados do domínio do espaço discreto para o domínio da frequência discreta através da **Transformada de Fourier Discreta (DFT)**, cuja execução computacional otimizada utiliza o algoritmo da Transformada Rápida de Fourier (FFT).



#### Construção da Matriz de Fourier ($W_N$)
A DFT converte a sequência espectral mapeando o sinal em componentes de frequências harmônicas. O círculo trigonométrico complexo é fracionado em $N$ fatias ortogonais. A Transformada é calculada pela aplicação da Matriz de Fourier $W_N$, cujos elementos internos são determinados pelas raízes complexas da unidade:
$$W_N = e^{-j\frac{2\pi}{N}}$$
A matriz de transformação de dimensões $N \times N$, onde as linhas representam os índices de frequência $k$ e as colunas denotam os índices de espaço discreto $n$, é estruturada como:
$$\mathbf{W} = \begin{bmatrix} 1 & 1 & 1 & \dots & 1 \\ 1 & W_N^1 & W_N^2 & \dots & W_N^{(N-1)} \\ 1 & W_N^2 & W_N^4 & \dots & W_N^{2(N-1)} \\ \vdots & \vdots & \vdots & \ddots & \vdots \\ 1 & W_N^{(N-1)} & W_N^{2(N-1)} & \dots & W_N^{(N-1)(N-1)} \end{bmatrix}$$

O espectro complexo do sinal do vinho na frequência é obtido pela multiplicação matricial:
$$X[k] = \mathbf{W} \cdot x[n]$$

#### O Teorema da Convolução de Oppenheim
A grande vantagem teórica e prática dessa migração é amparada pelo Teorema da Convolução. A complexa e trabalhosa operação de convolução (que envolve espelhar, deslocar ponto a ponto e somar matrizes no espaço) colapsa em uma operação de **Multiplicação Direta Elemento a Elemento** no domínio da frequência. 

O fluxo de processamento harmônico segue estritamente os seguintes passos resolutivos:
1. **Zero-Padding Geral:** Redimensiona o sinal do vinho $x[n]$ e a resposta ao impulso do filtro $h[n]$ preenchendo-os com zeros até o tamanho linear $N_{\text{total}} = N + M - 1$.
2. **Transformação do Sinal:** Aplica a FFT no sinal expandido para obter sua representação harmônica: $X[k] = \text{FFT}\{x[n]\}$.
3. **Transformação do Filtro:** Aplica a FFT na resposta ao impulso do filtro para obter a resposta em frequência do sistema: $H[k] = \text{FFT}\{h[n]\}$.
4. **Filtragem na Frequência:** Multiplica os dois vetores resultantes ponto a ponto (multiplicação escalar simples):
   $$Y[k] = X[k] \cdot H[k] \implies \begin{bmatrix} Y[0] \\ Y[1] \\ \vdots \\ Y[N_{\text{total}}-1] \end{bmatrix} = \begin{bmatrix} X[0] \cdot H[0] \\ X[1] \cdot H[1] \\ \vdots \\ X[N_{\text{total}}-1] \cdot H[N_{\text{total}}-1] \end{bmatrix}$$
5. **Transformação Inversa:** Retorna o sinal filtrado para o domínio espacial discreto aplicando a Transformada de Fourier Discreta Inversa (IDFT):
   $$y_{\text{filtrado}}[n] = \text{IFFT}\{Y[k]\}$$

Esse método de processamento em frequência contorna a necessidade de construir imensas matrizes circulantes na memória do computador, otimizando a complexidade computacional de $\mathcal{O}(N^2)$ para $\mathcal{O}(N \log N)$ através da FFT, entregando um resultado rigorosamente idêntico ao cálculo realizado no espaço discreto e consolidando o fechamento teórico da disciplina de Análise de Sinais e Sistemas aplicada a dados reais de engenharia.