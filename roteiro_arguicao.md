# CrediSmart — roteiro de apresentação (10 minutos) e arguição

> Material para estudo: não substitui a leitura de `main.py` **e dos módulos em `credismart/`**. Personalize a fala com o que o grupo realmente executou e verificou.

## Sequência sugerida — 10 minutos

| Tempo | Tema | O que demonstrar |
|---|---|---|
| 0:00–0:50 | Problema | Explicar as três etapas: risco por MLP, limite por fuzzy, otimização por AG. |
| 0:50–1:50 | Dados | Os cinco atributos, alvo y=1, seed 2026, split 1400/300/300, log renda e z-score só do treino. |
| 1:50–3:40 | MLP | Uma camada oculta `tanh`, saída `sigmoide`, BCE, derivada `(p-y)/m`, backprop, teste XOR e gráfico de perdas. |
| 3:40–4:40 | Comparativos | Apresentar a tabela das quatro arquiteturas e discutir custos de FN/FP. |
| 4:40–6:30 | Fuzzy | Mostrar 3 funções por variável, 9 regras e uma execução passo a passo com mínimo, máximo, centroide. |
| 6:30–8:00 | AG | Explicar cromossomo, F1 na validação, torneio 3, crossover, mutação 30%, elitismo 2, convergência. |
| 8:00–9:10 | Integração | Percorrer os cinco clientes de teste e a política hipotética de teto de R$ 20.000. |
| 9:10–10:00 | Ética e conclusão | Limitações da base sintética, viés, falsas aprovações, revisão humana e ganho observado na amostra. |

## Perguntas prováveis e respostas essenciais

**1. Por que a MLP aprende XOR e o Perceptron não?**  
XOR não é linearmente separável. O Perceptron produz apenas uma fronteira linear; a camada oculta com ativação não linear combina múltiplas fronteiras. Os resultados para `[0,0], [0,1], [1,0], [1,1]` foram `[0,1,1,0]`.

**2. O que acontece no forward?**  
A entrada passa pela multiplicação `X @ W1 + b1`, pela `tanh`, depois `A1 @ W2 + b2` e pela sigmoide para produzir probabilidade entre 0 e 1.

**3. O que é backpropagation?**  
É calcular derivadas da perda, da saída para trás, usando a regra da cadeia. Com BCE e sigmoide, `dZ2 = (p - y)/m`. Os gradientes de W1, b1, W2 e b2 atualizam os parâmetros por descida do gradiente.

**4. Como impedir vazamento de dados?**  
Ajustamos a média e o desvio **só com treino** e aplicamos a mesma transformação aos outros conjuntos. O AG avalia F1 na validação, e o teste só é usado no relatório final.

**5. O que significam precisão, recall e F1?**  
Precisão = `TP/(TP+FP)`: dos marcados inadimplentes, quantos eram. Recall = `TP/(TP+FN)`: dos inadimplentes reais, quantos achamos. F1 = média harmônica de precisão e recall.

**6. Qual erro é mais caro?**  
Na perspectiva de perda financeira por empréstimo não pago, em geral o falso negativo (`y=1`, mas previsto `0`), pois aprovaria um inadimplente. Porém o falso positivo pode prejudicar clientes adimplentes, causar exclusão e perda de receita. O trade-off deve ser definido com custos e critérios de justiça, não apenas F1.

**7. Por que escolher Mamdani?**  
É interpretável, com regras linguísticas legíveis. O risco e o comprometimento são convertidos em graus de pertinência, combinados por mínimos; as saídas são agregadas por máximo e defuzzificadas por centroide.

**8. Como calcular o exemplo fuzzy do trabalho?**  
Para cliente #145: risco aproximado 0,0868 e comprometimento 0,3389. Risco baixo tem pertinência 1,000; comprometimento baixo 0,4443 e médio 0,4631. As duas regras relevantes ativam saída alta em 0,4443 e média em 0,4631. O centroide da agregação é 64,91%, cerca de R$ 12.982,20 sobre teto hipotético de R$ 20.000.

**9. Como o AG representa os hiperparâmetros?**  
Cada cromossomo tem `(quantidade de neurônios, taxa de aprendizado, quantidade de épocas)`. A aptidão é o F1 calculado na validação depois de treinar a MLP no treino com esses genes.

**10. O que são seleção, crossover, mutação e elitismo?**  
Seleção por torneio de 3 favorece indivíduos com F1 maior. Crossover combina genes dos pais. Mutação perturba genes para explorar soluções novas. Elitismo copia os 2 melhores para a geração seguinte, evitando perder bons indivíduos.

**11. A MLP otimizada é sempre melhor?**  
Não. No nosso teste o F1 passou de 0,8156 para 0,8556, mas pode haver variância de amostragem e sobreajuste indireto à validação. É preciso repetir em amostras externas, medir incerteza e monitorar o desempenho.

**12. O que é preciso para usar a solução no mercado real?**  
Dados reais com consentimento/base legal, validação externa e temporal, calibração de probabilidades, auditoria de equidade, avaliação de custo de erros, monitoramento, explicabilidade e revisão humana de decisões.

## Funções que cada integrante precisa localizar no código

- `credismart/dados.py`: `gerar_dados`, `separar_padronizar` — geração, divisão e z-score.
- `credismart/modelos.py`: `MLP.forward`, `MLP.perda_logits`, `MLP.fit`, `PerceptronRosenblatt.fit`, `metricas` — treinamento e avaliação.
- `credismart/fuzzy.py`: `triangular`, `trapezoidal`, `Mamdani.inferir` — pertinência e centroide.
- `credismart/genetico.py`: `AlgoritmoGenetico.aptidao`, `torneio`, `cruzamento`, `mutacao`, `executar` — evolução.
- `credismart/graficos.py`: gráficos exigidos no enunciado.
- `main.py`: `main` — orquestração do pipeline, avaliação e cinco exemplos.
- `tests/test_algoritmos.py`: testes dos gradientes da MLP, do XOR e da lógica fuzzy.
