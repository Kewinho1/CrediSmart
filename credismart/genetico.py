"""Algoritmo genético manual para seleção de hiperparâmetros da MLP."""
from dataclasses import dataclass, asdict
import numpy as np
from .config import SEED
from .modelos import MLP, metricas

@dataclass(frozen=True)
class Cromossomo:
    ocultos: int
    taxa: float
    epocas: int


class AlgoritmoGenetico:
    def __init__(self, Xtr, ytr, Xva, yva, populacao=10, geracoes=10, seed=2026):
        if populacao < 10 or geracoes < 10:
            raise ValueError("O enunciado exige >=10 individuos e >=10 geracoes.")
        self.Xtr, self.ytr, self.Xva, self.yva = Xtr,ytr,Xva,yva
        self.n, self.g = populacao, geracoes
        self.rng = np.random.default_rng(seed)
        self.cache = {}
        self.historico = []

    @staticmethod
    def reparar(c):
        return Cromossomo(ocultos=int(np.clip(c.ocultos,4,32)),
                          taxa=round(float(np.clip(c.taxa,0.025,0.40)),4),
                          epocas=int(np.clip(c.epocas,70,220)))

    def aleatorio(self):
        return self.reparar(Cromossomo(
            int(self.rng.integers(4,33)),
            float(np.exp(self.rng.uniform(np.log(.025),np.log(.4)))),
            int(self.rng.integers(70,221))))

    def aptidao(self, crom):
        if crom not in self.cache:
            # Semente fixa: comparacao justa e reproduzivel dos hiperparametros.
            rede = MLP(self.Xtr.shape[1], crom.ocultos, crom.taxa, seed=SEED)
            rede.fit(self.Xtr,self.ytr,epocas=crom.epocas, seed=SEED)
            pred = rede.predict(self.Xva)
            self.cache[crom] = metricas(self.yva,pred)["f1"]
        return self.cache[crom]

    def torneio(self, populacao, k=3):
        ids = self.rng.choice(len(populacao),size=k,replace=False)
        return max((populacao[int(i)] for i in ids),key=self.aptidao)

    def cruzamento(self, a, b):
        # Crossover uniforme para genes discretos e aritmetico para a taxa.
        t = self.rng.random()
        filho = Cromossomo(
            a.ocultos if self.rng.random() < .5 else b.ocultos,
            t*a.taxa + (1-t)*b.taxa,
            a.epocas if self.rng.random() < .5 else b.epocas)
        return self.reparar(filho)

    def mutacao(self,c,prob=.30):
        h, lr, ep = c.ocultos,c.taxa,c.epocas
        if self.rng.random() < prob: h += int(self.rng.choice([-6,-3,-1,1,3,6]))
        if self.rng.random() < prob: lr *= float(np.exp(self.rng.normal(0,.35)))
        if self.rng.random() < prob: ep += int(self.rng.choice([-40,-20,-10,10,20,40]))
        return self.reparar(Cromossomo(h,lr,ep))

    def executar(self):
        pop = [self.aleatorio() for _ in range(self.n)]
        for geracao in range(self.g):
            ordenados = sorted(pop,key=self.aptidao,reverse=True)
            scores = [self.aptidao(c) for c in pop]
            self.historico.append({"geracao":geracao+1,"melhor":float(max(scores)),
                                   "media":float(np.mean(scores)),
                                   "melhor_cromossomo":asdict(ordenados[0])})
            print(f"  AG geracao {geracao+1:2d}/{self.g}: "
                  f"F1 melhor={max(scores):.3f} media={np.mean(scores):.3f}",flush=True)
            # 2 elites; nao criar uma 11a geracao apos a avaliacao final.
            if geracao < self.g - 1:
                proxima = ordenados[:2]
                while len(proxima) < self.n:
                    pa = self.torneio(pop)
                    pb = self.torneio(pop)
                    proxima.append(self.mutacao(self.cruzamento(pa,pb)))
                pop = proxima
        melhor = max(self.cache,key=self.aptidao)
        return melhor, self.aptidao(melhor)

