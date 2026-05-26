
# Estrutura Sugerida da Apresentação (15 min — 3 integrantes)

**Objetivo geral:** apresentar o pipeline completo de Processamento Digital de Sinais aplicado a espectros FTIR de vinhos, conectando rigor matemático de Sinais e Sistemas com interpretação físico-química.

**Tempo total:** ~15 minutos  
**Quantidade sugerida:** 16–18 slides  
**Estratégia:** 1 ideia forte por slide + fala aprofundando + bastante visual.

---

# Integrante 1 — Problema, Modelagem e Pré-processamento (~5 min)

## Slide 1 — Título e Motivação
### Tema do Trabalho
**Processamento Digital de Sinais aplicado à análise espectral FTIR de vinhos**

### Problema
Os espectros FTIR apresentam:
- Ruído de medição
- Variações entre réplicas
- Dificuldade em extrair informações químicas diretamente

### Objetivo
Aplicar técnicas de PDS para:
- Reduzir ruído
- Preservar informações relevantes
- Extrair métricas químicas comparáveis

**Tempo sugerido:** ~40 s

---

## Slide 2 — O que é FTIR?
### Fundamentação Experimental
Explicar brevemente:
- FTIR mede absorbância espectral
- Cada composto químico possui bandas características
- O espectro funciona como uma “assinatura química” do vinho

### Mostrar
- Um espectro FTIR real
- Eixos:
  - Número de onda (cm⁻¹)
  - Absorbância

**Mensagem principal:**
> O problema é transformar esse espectro em informação útil.

**Tempo sugerido:** ~50 s

---

## Slide 3 — Modelagem do Sinal
### Interpretação sob Sinais e Sistemas

Modelagem do espectro:

\[
x[n] = v[n] + e[n]
\]

Onde:

- \(v[n]\): sinal real (componentes químicos do vinho)
- \(e[n]\): ruído do sensor

### Explicar
- O número de onda é tratado como variável discreta \(n\)
- O FTIR vira um problema de processamento de sinais

### Mostrar
- Exemplo de espectro ruidoso

**Mensagem principal:**
> Nosso trabalho consiste em recuperar o sinal relevante do ruído.

**Tempo sugerido:** ~50 s

---

## Slide 4 — Pipeline Geral do Projeto
### Arquitetura do Sistema

Fluxograma:

**Triplicatas → Média → Filtragem → Segmentação Química → Métricas → Comparação dos Vinhos**

### Explicar rapidamente cada bloco
1. Média das réplicas
2. Suavização do espectro
3. Isolamento de regiões químicas
4. Extração de métricas

**Mensagem principal:**
> O trabalho foi estruturado como uma cascata de sistemas discretos.

**Tempo sugerido:** ~40 s

---

## Slide 5 — Média das Triplicatas
### Primeiro Estágio do Sistema

Mostrar:
- Rep1
- Rep2
- Rep3
- Média resultante

### Conexão com linearidade
Apresentar rapidamente:

\[
y[n] =
\frac{x_1[n]+x_2[n]+x_3[n]}{3}
\]

### Explicar
- Ruído aleatório tende a cancelar
- Sinal real é reforçado

**Mensagem principal:**
> Aplicamos o princípio da superposição para reduzir variabilidade experimental.

**Tempo sugerido:** ~1 min

---

## Slide 6 — Resultado da Média
### Antes vs Depois

Mostrar gráfico comparativo:
- Réplicas individuais
- Curva média

### Resultado observado
- Redução do ruído inter-amostral
- Espectro mais estável

**Mensagem principal:**
> A média melhora a relação sinal-ruído antes da filtragem.

**Tempo sugerido:** ~1 min

---

# Integrante 2 — Filtragem e Processamento Digital (~5 min)

## Slide 7 — Problema do Ruído Intra-amostral
### Motivação da Filtragem

Mostrar:
- Espectro ainda com oscilações locais

### Explicar
Mesmo após a média:
- Persistem pequenas flutuações
- Essas oscilações dificultam identificação de bandas químicas

**Mensagem principal:**
> Precisávamos suavizar o sinal sem destruir os picos importantes.

**Tempo sugerido:** ~30 s

---

## Slide 8 — Filtro de Média Móvel
### Primeira Estratégia

Explicar intuitivamente:
- Média entre vizinhos
- Atua como filtro passa-baixas

Equação simples:

\[
y[n] =
\frac{1}{M}
\sum_{k=0}^{M-1}
x[n-k]
\]

### Mostrar
Visual da janela móvel

### Vantagem
- Simples
- Remove ruído

### Limitação
- Pode achatar picos

**Tempo sugerido:** ~1 min

---

## Slide 9 — Filtro Savitzky–Golay
### Segunda Estratégia

Explicar intuitivamente:
- Ajusta um polinômio local
- Suaviza preservando formato do espectro

### Mostrar
Visual da regressão polinomial local

### Vantagem
- Preserva altura e largura dos picos

**Mensagem principal:**
> Mais adequado para sinais químicos e espectrais.

**Tempo sugerido:** ~1 min

---

## Slide 10 — Comparação dos Filtros
### Resultado Experimental

Mostrar:

**Original × Média Móvel × Savitzky–Golay**

### Discutir
- Qual remove melhor ruído
- Qual preserva melhor picos

### Justificativa da escolha final

**Mensagem principal:**
> O Savitzky–Golay apresentou melhor preservação das características químicas.

**Tempo sugerido:** ~1 min 20 s

---

## Slide 11 — Interpretação em Sinais e Sistemas
### Visão Conceitual

Explicar de forma leve:

Os filtros atuam como:

**Filtros Passa-Baixas**

Ou seja:
- Reduzem componentes de alta frequência
- Preservam tendências do sinal

### Evitar
❌ ROC  
❌ Polos e zeros detalhados  
❌ Demonstrações extensas de Z-transform

**Mensagem principal:**
> O processamento reduz ruído sem perder informação relevante.

**Tempo sugerido:** ~1 min

---

# Integrante 3 — Segmentação Química e Resultados (~5 min)

## Slide 12 — Regiões Químicas do Espectro
### Segmentação por Wavenumbers

Mostrar gráfico do **degrau unitário deslocado** sobreposto ao espectro.

Faixas:

- Açúcares: 900–1150 cm⁻¹
- Ácidos orgânicos: ~1200 cm⁻¹
- Polifenóis: 1400–1600 cm⁻¹
- Proteínas: ~1650 cm⁻¹
- Ésteres: 1730–1750 cm⁻¹

### Explicar
Cada faixa corresponde a vibrações moleculares específicas.

**Mensagem principal:**
> Isolamos apenas regiões de interesse químico.

**Tempo sugerido:** ~1 min

---

## Slide 13 — Aplicação do Passa-Banda
### Isolamento das Regiões

Mostrar:
- Espectro completo
- Região isolada

### Explicar
Fora da banda:
- valor zerado

Dentro da banda:
- sinal preservado

**Mensagem principal:**
> Criamos filtros espaciais para focar apenas nas regiões relevantes.

**Tempo sugerido:** ~45 s

---

## Slide 14 — Extração de Métricas
### Como quantificamos os compostos?

Duas métricas:

### Pico
- Intensidade local
- Proeminência espectral

### Área
- Energia total da banda
- Integração trapezoidal

Conexão física:

\[
A = \varepsilon b c
\]

(Lei de Beer–Lambert)

**Mensagem principal:**
> A absorbância pode indicar concentração relativa do composto.

**Tempo sugerido:** ~1 min

---

## Slide 15 — Resultados Obtidos
### Comparação entre Vinhos

Mostrar:
- Tabela
ou
- gráfico radar
ou
- barras comparativas

Comparar:
- Açúcares
- Polifenóis
- Ácidos
- Ésteres
- Proteínas

### Explicar
O que os resultados sugerem.

**Tempo sugerido:** ~1 min

---

## Slide 16 — Conclusões
### Principais Achados

✔ Redução do ruído experimental

✔ Preservação de características espectrais relevantes

✔ Segmentação química eficiente

✔ Extração de métricas comparáveis entre amostras

### Conclusão final
> O uso de Processamento Digital de Sinais permitiu transformar espectros FTIR em informações quantitativas relevantes sobre composição química do vinho.

**Tempo sugerido:** ~40 s

---

## Slide 17 — Limitações e Trabalhos Futuros (Opcional)
### Próximos Passos

- Mais amostras
- Novas regiões químicas
- Classificação automática
- PCA / Machine Learning
- Diferenciação automática de vinhos

**Tempo sugerido:** ~30 s

---

## Slide 18 — Perguntas
**Obrigado!**