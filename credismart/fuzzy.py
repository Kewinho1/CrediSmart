"""Inferência Mamdani manual: pertinência, regras, agregação e centroide."""
import numpy as np
from .config import integral_trapezoidal

def triangular(x, a, b, c):
    x = np.asarray(x, dtype=float)
    subida = np.where(b>a, (x-a)/max(b-a,1e-12), (x>=b).astype(float))
    descida = np.where(c>b, (c-x)/max(c-b,1e-12), (x<=b).astype(float))
    return np.maximum(0.0, np.minimum(1.0, np.minimum(subida, descida)))


def trapezoidal(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    subida = np.where(b>a, (x-a)/max(b-a,1e-12), (x>=a).astype(float))
    descida = np.where(d>c, (d-x)/max(d-c,1e-12), (x<=d).astype(float))
    return np.maximum(0.0, np.minimum(1.0, np.minimum(subida, descida)))


class Mamdani:
    """Regra AND=min; composicao por corte=min; agregacao=max; centroide."""
    TERMOS = ("baixo", "medio", "alto")
    # 9 regras: risco (linha), comprometimento (coluna) => limite
    REGRAS = (
        ("alto", "medio", "baixo"),
        ("medio", "medio", "baixo"),
        ("baixo", "baixo", "baixo"),
    )

    def __init__(self, resolucao=1001):
        self.universo = np.linspace(0,100,resolucao)

    def conjuntos_entrada(self, x):
        return {"baixo":trapezoidal(x,0,0,0.20,0.45),
                "medio":triangular(x,0.20,0.50,0.80),
                "alto":trapezoidal(x,0.55,0.80,1,1)}

    def conjuntos_saida(self, x):
        return {"baixo":trapezoidal(x,0,0,15,40),
                "medio":triangular(x,25,50,75),
                "alto":trapezoidal(x,60,85,100,100)}

    def inferir(self, risco, comprometimento, detalhar=False):
        risco, comprometimento = float(risco), float(comprometimento)
        if not (0 <= risco <= 1 and 0 <= comprometimento <= 1):
            raise ValueError("Ambas as entradas devem estar em [0, 1].")
        mu_r = self.conjuntos_entrada(risco)
        mu_c = self.conjuntos_entrada(comprometimento)
        mu_l = self.conjuntos_saida(self.universo)
        agregado = np.zeros_like(self.universo)
        regras = []
        for i, t_r in enumerate(self.TERMOS):
            for j, t_c in enumerate(self.TERMOS):
                termo_saida = self.REGRAS[i][j]
                ativacao = float(min(mu_r[t_r], mu_c[t_c]))
                cortado = np.minimum(ativacao, mu_l[termo_saida])
                agregado = np.maximum(agregado, cortado)
                regras.append({"risco":t_r, "comprometimento":t_c,
                               "saida":termo_saida, "ativacao":ativacao})
        area = float(integral_trapezoidal(agregado, self.universo))
        if area <= 1e-12:
            raise RuntimeError("Nenhuma regra foi ativada; verificar cobertura dos conjuntos.")
        centroide = float(integral_trapezoidal(agregado*self.universo,self.universo)/area)
        if detalhar:
            return {"risco":risco, "comprometimento":comprometimento,
                    "fuzzificacao_risco":{k:float(v) for k,v in mu_r.items()},
                    "fuzzificacao_comprometimento":{k:float(v) for k,v in mu_c.items()},
                    "regras":regras, "area":area,
                    "momento":float(integral_trapezoidal(agregado*self.universo,self.universo)),
                    "centroide_percentual":centroide}
        return centroide

