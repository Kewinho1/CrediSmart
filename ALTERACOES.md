# Alterações da versão organizada

## Atualização de geração das figuras

- O relatório agora executa novamente o experimento antes de montar o PDF.
- Matplotlib salva as seis figuras em uma pasta exclusiva `figuras/execucao_<id>/` para cada execução.
- `resultados.json` registra a pasta da execução atual; o gerador do PDF lê as figuras desse caminho, sem usar imagens antigas.
- O README foi ajustado para que `python gerar_relatorio.py` seja o comando único de geração do experimento, dos gráficos e do PDF.

O conteúdo do link externo do Claude **não estava acessível**, portanto esta revisão foi baseada no **enunciado oficial** e no projeto executável já existente. Não se deve afirmar que as recomendações do Claude foram aplicadas sem consultar o texto delas.

## Melhorias efetuadas

1. `main.py` passou a conter a orquestração do experimento, enquanto os algoritmos foram separados por responsabilidade em `credismart/`.
2. `credismart/dados.py` mantém a função de geração da base sintética exatamente como no enunciado e o pré-processamento sem vazamento.
3. `credismart/modelos.py` contém a implementação NumPy da MLP e do Perceptron de Rosenblatt.
4. `credismart/fuzzy.py` reúne pertinência, nove regras, agregação min/max e centroide.
5. `credismart/genetico.py` agrupa a codificação, avaliação e evolução dos cromossomos.
6. `credismart/graficos.py` gera as seis figuras exigidas pelo trabalho.
7. `tests/test_algoritmos.py` acrescenta oito testes, incluindo **gradiente numérico por diferenças finitas** e o XOR.
8. `gerar_relatorio.py` passa a localizar fontes de forma portável, usando DejaVu ou o conjunto Vera disponibilizado pelo ReportLab.
9. README e roteiro de arguição foram atualizados com caminhos, comandos e verificação pré-entrega.
10. Resultados foram gerados novamente após a separação em módulos, sem mudanças no protocolo de treino, validação e teste.

## Verificações realizadas

- `python -m unittest discover -s tests -v` — **8 testes aprovados**.
- `python main.py` — **concluído sem erros**.
- `python gerar_relatorio.py` — **relatório de 8 páginas**.
- PDF renderizado e inspecionado — nenhuma sobreposição ou truncamento evidente.
- F1 da MLP manual: **0,8156**; F1 da MLP otimizada: **0,8556** (iguais aos resultados anteriores).

## Pendente

Para aderir especificamente às observações do Claude, é necessário **colar o texto da análise ou anexar capturas de tela**, porque o conteúdo do link `claude.ai/artifact/...` não pôde ser recuperado. Depois disso, conferir cada observação e verificar quais ajustes ainda faltam.
