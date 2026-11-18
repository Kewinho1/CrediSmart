# CrediSmart — Trabalho Prático Integrador de Inteligência Artificial

Centro Universitário Padre Anchieta · 2º semestre de 2026  
**Prazo:** 17/11/2026, às 23h59 · **Arguição:** 18/11/2026

## 1. Identificação do grupo (preencher antes da entrega)

| Integrante | RA |
|---|---|
| Aluno(a): Alessandra de Freitas  Bichara | 2405879 |
| Aluno(a): Kewin Lorente Magoga | 2403809 |
| Aluno(a): Livia Ferreira Rodrigues | 2408713 |
| Aluno(a): Manuella de Souza Filgueiras | 2404788 |

O gerador lê esta tabela automaticamente. Salve os nomes e RAs aqui antes de executar `python gerar_relatorio.py`; a capa e os metadados do PDF serão atualizados com esses dados.

## 2. O que o projeto faz

O fluxo completo usa **dados sintéticos → MLP → risco de inadimplência → Mamdani fuzzy → limite sugerido**. Um **algoritmo genético** busca hiperparâmetros da MLP usando **somente validação**, nunca o teste.

- **Parte 1:** dados, normalização, Perceptron, MLP manual com backpropagation, verificação XOR e comparação com regressão logística e MLP do scikit-learn.
- **Parte 2:** nove regras de inferência Mamdani, funções de pertinência triangulares/trapezoidais, operadores min/max e centroide.
- **Parte 3:** população de 10 indivíduos durante 10 gerações, aptidão F1 na validação, torneio, cruzamento, mutação e elitismo.
- **Parte 4:** pipeline integrado com cinco clientes, relatório de oito páginas, tabelas e gráficos.
- **Parte 5:** roteiro explicativo para apresentação e arguição.

**Importante:** os componentes centrais são implementados manualmente com **NumPy**; o `scikit-learn` aparece somente nos dois modelos comparativos permitidos pelo enunciado. Este protótipo **não é apropriado para decisões reais de concessão de crédito**.

## 3. Estrutura dos arquivos

```text
CrediSmart/
├── main.py                     # Ponto de entrada: executa todas as partes
├── credismart/
│   ├── config.py               # Caminhos, semente e integração numérica
│   ├── dados.py                # Função oficial da base e pré-processamento
│   ├── modelos.py              # MLP, Perceptron e métricas manuais
│   ├── fuzzy.py                # Funções de pertinência e Mamdani
│   ├── genetico.py             # Cromossomos, aptidão e operadores do AG
│   └── graficos.py             # Gráficos de análise e demonstração
├── tests/
│   └── test_algoritmos.py      # 8 testes de verificação matemática
├── figuras/                   # Nova pasta de gráficos em cada execução
├── resultados.json             # Valores numéricos da execução
├── gerar_relatorio.py          # Cria o PDF a partir dos resultados e gráficos
├── relatorio_tecnico.pdf       # Relatório final de 8 páginas
├── roteiro_arguicao.md        # Perguntas e apoio à explicação individual
├── requirements.txt           # Dependências
└── README.md
```

A separação por módulo segue as partes do enunciado e facilita localizar cada algoritmo durante a arguição. **`python gerar_relatorio.py` é o comando único para executar o experimento e atualizar o relatório.**

## 4. Como instalar e executar

Pré-requisito: **Python 3.10 ou superior**.

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python gerar_relatorio.py
```

**Linux ou macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python gerar_relatorio.py
```

`gerar_relatorio.py` executa o pipeline completo e recria `resultados.json`, as seis imagens com Matplotlib e o PDF. Cada execução grava as figuras em uma nova pasta `figuras/execucao_<id>/`, e o relatório usa exclusivamente as imagens dessa execução. Não há dependência dos PNGs antigos incluídos em versões anteriores do pacote. Como a semente e os dados são fixos pelo enunciado, os valores dos gráficos podem se repetir, embora as figuras sejam geradas novamente. O arquivo PDF pronto **já está incluído no ZIP**.

Para gerar apenas os resultados e os gráficos, sem atualizar o PDF, execute `python main.py`. Se executar `main.py` e depois `gerar_relatorio.py`, o experimento será executado duas vezes.

A suíte de testes inclui XOR, verificação dos gradientes da MLP por diferenças finitas, separação e padronização da base, lógica fuzzy e limites dos cromossomos. Os testes **não substituem** a execução completa do experimento.

## 5. Protocolo e decisões do experimento

| Item | Definição |
|---|---|
| Dados | Função **exatamente** como no enunciado; `n=2000`, `seed=2026` |
| Divisão | `default_rng(42).permutation`: 1.400 treino, 300 validação, 300 teste |
| Preparação | `log(renda)`, média e desvio **apenas no treino**, z-score para os três conjuntos |
| MLP manual | 16 neurônios ocultos, taxa 0,12, 140 épocas, minibatches de até 128 |
| Aptidão AG | F1 na **validação**; o teste é usado somente na avaliação final |
| Genes AG | Neurônios 4–32, taxa 0,025–0,40, épocas 70–220 |
| Operadores AG | Torneio de 3, cruzamento uniforme/aritmético, mutação de 30% por gene, 2 elites |
| Decisão binária | Limiar 0,5, fixado para comparação entre os modelos |
| Limite ilustrativo | **R$ 20.000**, apenas como exemplo, não aprendido na base |

## 6. Resultados reproduzidos

| Modelo | Acurácia | Precisão | Recall | F1 |
|---|---:|---:|---:|---:|
| Perceptron manual | 81,7% | 72,3% | 70,1% | 71,2% |
| Regressão logística (sklearn) | 89,7% | 90,2% | 76,3% | 82,7% |
| MLP (sklearn) | 89,7% | 90,2% | 76,3% | 82,7% |
| MLP manual | 89,0% | 89,0% | 75,3% | **81,6%** |
| MLP otimizada pelo AG | 91,3% | 92,8% | 79,4% | **85,6%** |

O AG encontrou **22 neurônios, taxa 0,3688 e 107 épocas**. O ganho observado foi de aproximadamente **4 pontos percentuais em F1 no teste** sobre o ajuste manual. Não há garantia de repetição desse ganho em outra amostra; os mesmos 300 exemplos de validação foram consultados várias vezes pelo AG.

## 7. Conferência para a entrega

- [ ] Preencher nomes e RAs nesta página e na capa do PDF.
- [ ] Executar os **8 testes** e o comando `python gerar_relatorio.py` em uma máquina do grupo.
- [ ] Conferir gráficos, tabela dos 5 clientes, relatório de 6–10 páginas e arquivo ZIP.
- [ ] Revisar **declaração de uso de IA** no relatório e refletir corretamente quais ferramentas foram usadas.
- [ ] Verificar se todos conseguem explicar forward, backprop, XOR, centróide, aptidão, seleção, cruzamento e mutação.
- [ ] Entregar até o horário indicado no enunciado.

## 8. Declaração de uso de IA generativa

Foram utilizadas ferramentas de IA generativa da OpenAI, incluindo ChatGPT e Codex, como apoio na implementação e revisão do código, criação de testes, geração de gráficos, organização da documentação e elaboração do relatório. Todo o conteúdo foi revisado pelos integrantes, que assumem responsabilidade integral pelo trabalho apresentado.
