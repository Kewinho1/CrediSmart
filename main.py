#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CrediSmart — orquestração do experimento acadêmico.

Execute com: python main.py
Cada algoritmo está implementado manualmente em credismart/.
O scikit-learn é usado SOMENTE nos dois classificadores comparativos.
"""
from __future__ import annotations
import json
from dataclasses import asdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from credismart.config import BASE, SEED
from credismart.dados import gerar_dados, separar_padronizar
from credismart.modelos import MLP, PerceptronRosenblatt, metricas
from credismart.fuzzy import Mamdani
from credismart.genetico import Cromossomo, AlgoritmoGenetico
from credismart.graficos import (
    estilo, grafico_perda, grafico_xor, grafico_pertinencia,
    grafico_superficie, grafico_ag, grafico_comparativo,
)

def main():
    estilo()
    dados, Y, raw, parametros = separar_padronizar()
    Xtr,Xva,Xte=(dados[k] for k in ["treino","validacao","teste"])
    ytr,yva,yte=(Y[k] for k in ["treino","validacao","teste"])
    print("Divisao: treino 1400, validacao 300, teste 300")
    print("Taxa de inadimplencia:", {k:round(float(Y[k].mean()),4) for k in Y})

    # XOR: o Perceptron linear nao resolve a nao separabilidade linear.
    xx=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
    yy=np.array([0,1,1,0])
    xor_mlp=MLP(2,8,taxa=.35,seed=29).fit(xx,yy,epocas=7500,lote=4,seed=29)
    xor_prob=xor_mlp.predict_proba(xx)
    xor_pred=xor_mlp.predict(xx)
    print("XOR: probabilidades",np.round(xor_prob,4),"predicoes",xor_pred)
    if not np.array_equal(xor_pred, yy):
        raise AssertionError("MLP nao aprendeu XOR. Ajustar hiperparametros do teste.")
    grafico_xor(xor_mlp)

    # Ajuste manual fixado antes de olhar teste, para comparacao honesta com AG.
    config_manual=Cromossomo(16,.12,140)
    rede_manual=MLP(5,config_manual.ocultos,config_manual.taxa,seed=SEED)
    rede_manual.fit(Xtr,ytr,epocas=config_manual.epocas,seed=SEED,validacao=(Xva,yva))
    grafico_perda(rede_manual)
    print("MLP manual - F1 validacao:",round(metricas(yva,rede_manual.predict(Xva))["f1"],4))

    # Apenas modelos comparativos podem usar scikit-learn.
    modelos={
        "Perceptron": PerceptronRosenblatt().fit(Xtr,ytr),
        "Regressao Logistica": LogisticRegression(max_iter=2000,random_state=SEED).fit(Xtr,ytr),
        "MLP sklearn": MLPClassifier(hidden_layer_sizes=(16,),activation="tanh",
                                      solver="adam",max_iter=500,random_state=SEED).fit(Xtr,ytr),
        "MLP manual": rede_manual,
    }
    comparativo={nome:metricas(yte,mdl.predict(Xte)) for nome,mdl in modelos.items()}
    grafico_comparativo(comparativo)

    fuzzy=Mamdani()
    grafico_pertinencia(fuzzy)
    grafico_superficie(fuzzy)

    # Testes unitarios minimos de extremos e cobertura.
    for i in np.linspace(0,1,11):
        for j in np.linspace(0,1,11):
            v=fuzzy.inferir(float(i),float(j))
            assert 0 <= v <= 100, (i,j,v)
    assert fuzzy.inferir(.05,.05) > fuzzy.inferir(.95,.95)

    print("Executando AG (10 individuos x 10 geracoes)...",flush=True)
    ag=AlgoritmoGenetico(Xtr,ytr,Xva,yva,populacao=10,geracoes=10)
    melhor, melhor_f1_val=ag.executar()
    grafico_ag(ag.historico)
    rede_otimizada=MLP(5,melhor.ocultos,melhor.taxa,seed=SEED).fit(
        Xtr,ytr,epocas=melhor.epocas,seed=SEED)
    metricas_otimizada=metricas(yte,rede_otimizada.predict(Xte))
    pred_manual=rede_manual.predict(Xte)
    p_otimizada=rede_otimizada.predict_proba(Xte)

    # Escolha pre-estabelecida, cobrindo diferentes riscos e compromissos.
    ordenacao=np.argsort(p_otimizada)
    indices=[int(ordenacao[int(k*(len(ordenacao)-1)/6)]) for k in range(1,6)]
    indices=[*dict.fromkeys(indices)]  # sem repeticao
    limite_maximo_reais=20000.0  # cenario ilustrativo, NAO e criterio empirico da base
    exemplos=[]
    for idx in indices:
        linha=raw["teste"][idx]
        p=float(p_otimizada[idx]); comp=float(linha[2])
        percentual=fuzzy.inferir(p,comp)
        exemplos.append({"id_teste":idx,"renda_reais":float(linha[0]),"idade":int(linha[1]),
                         "comprometimento":comp,"atrasos":int(linha[3]),
                         "tempo_emprego":float(linha[4]),"inadimplente_real":int(yte[idx]),
                         "probabilidade_inadimplencia":p,
                         "limite_percentual":percentual,
                         "limite_reais":percentual/100*limite_maximo_reais})
    # Exemplo de calculo com cliente real do teste, sem usa-lo para treinar/ajustar.
    escolhido=exemplos[2]
    detalhamento=fuzzy.inferir(escolhido["probabilidade_inadimplencia"],
                               escolhido["comprometimento"],detalhar=True)

    saida={
        "seed_dados":SEED,"seed_split":42,"tamanhos":{k:len(Y[k]) for k in Y},
        "proporcao_y1":{k:float(Y[k].mean()) for k in Y},
        "padronizacao_treino":parametros,
        "xor":{"entradas":xx.tolist(),"esperado":yy.tolist(),"probabilidades":xor_prob.tolist(),
               "predicoes":xor_pred.tolist()},
        "configuracao_manual":asdict(config_manual),
        "f1_validacao_manual":metricas(yva,rede_manual.predict(Xva))["f1"],
        "metricas_teste_comparativo":comparativo,
        "ag":{"populacao":ag.n,"geracoes":ag.g,"melhor":asdict(melhor),
              "melhor_f1_validacao":melhor_f1_val,"avaliacoes_distintas":len(ag.cache),
              "historico":ag.historico},
        "metricas_teste_otimizada":metricas_otimizada,
        "comparacao_f1_teste_delta":metricas_otimizada["f1"] - comparativo["MLP manual"]["f1"],
        "limite_maximo_ilustrativo_reais":limite_maximo_reais,
        "pipeline_cinco_clientes":exemplos,
        "exemplo_fuzzy_passo_a_passo":detalhamento,
        "observacao":"Resultados apenas academicos, com base sintetica e sem avaliacao de vies por grupo."}
    (BASE/"resultados.json").write_text(json.dumps(saida,indent=2,ensure_ascii=False),encoding="utf-8")
    print("\nMETRICAS NO TESTE")
    for nome,m in comparativo.items():
        print(f"  {nome:20s} Acc {m['acuracia']:.3f} P {m['precisao']:.3f} "
              f"R {m['recall']:.3f} F1 {m['f1']:.3f}")
    print("  MLP otimizada       ",metricas_otimizada)
    print("Melhor cromossomo:",melhor,"F1 val:",melhor_f1_val)
    print("Arquivos salvos em:",BASE)
    return saida


if __name__ == "__main__":
    main()
