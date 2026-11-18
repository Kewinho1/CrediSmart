"""Geração dos dados originais e pré-processamento sem vazamento."""
import numpy as np

def gerar_dados(n=2000, seed=2026):
    rng=np.random.default_rng(seed)
    renda=rng.lognormal(8.2,0.5,n)
    idade=rng.integers(18,71,n)
    comp=np.clip(rng.beta(2,3,n),0,1)
    atrasos=rng.poisson(0.8,n)
    emprego=np.clip(rng.exponential(5,n),0,40)
    z=(-2.0+4.0*comp**2+0.9*atrasos-0.35*np.log(renda/2000)
      -0.06*emprego+0.0012*(idade-40)**2+1.5*comp*(atrasos>1)
      +rng.normal(0,0.6,n))
    y=(z>0).astype(int)
    X=np.column_stack([renda,idade,comp,atrasos,emprego]).astype(float)
    return X,y


def separar_padronizar(seed_dados=2026, seed_split=42):
    X, y = gerar_dados(seed=seed_dados)
    perm = np.random.default_rng(seed_split).permutation(len(y))
    tr, va, te = perm[:1400], perm[1400:1700], perm[1700:2000]
    assert len(set(tr) & set(va)) == len(set(tr) & set(te)) == len(set(va) & set(te)) == 0
    Xraw = {"treino": X[tr].copy(), "validacao": X[va].copy(), "teste": X[te].copy()}
    Y = {"treino": y[tr].copy(), "validacao": y[va].copy(), "teste": y[te].copy()}
    transformed = {}
    for k, arr in Xraw.items():
        a = arr.copy()
        a[:, 0] = np.log(a[:, 0])  # log somente na renda, ANTES do z-score
        transformed[k] = a
    media = transformed["treino"].mean(axis=0)
    desvio = transformed["treino"].std(axis=0)
    desvio[desvio == 0.0] = 1.0
    dados = {k: (v-media)/desvio for k, v in transformed.items()}
    return dados, Y, Xraw, {"media":media.tolist(), "desvio":desvio.tolist()}

