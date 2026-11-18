"""Gráficos usados na análise e no relatório."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from .config import FIG

def estilo():
    plt.rcParams.update({"figure.dpi":130,"font.size":10,"axes.spines.top":False,
                         "axes.spines.right":False,"axes.grid":True,"grid.alpha":.17})


def grafico_perda(mlp):
    fig,ax = plt.subplots(figsize=(8,3.8))
    ax.plot(mlp.historico["treino"],label="Treino",linewidth=2)
    ax.plot(mlp.historico["validacao"],label="Validacao",linewidth=2)
    ax.set(xlabel="Epoca",ylabel="Entropia cruzada binaria",title="Curva de perda da MLP manual")
    ax.legend();fig.tight_layout();fig.savefig(FIG/"perda_mlp.png");plt.close(fig)


def grafico_xor(rede):
    xx, yy = np.meshgrid(np.linspace(-.35,1.35,140),np.linspace(-.35,1.35,140))
    grid = np.c_[xx.ravel(),yy.ravel()]
    zz = rede.predict_proba(grid).reshape(xx.shape)
    fig,ax = plt.subplots(figsize=(5,4))
    im=ax.contourf(xx,yy,zz,levels=np.linspace(0,1,11),cmap="RdYlBu_r",vmin=0,vmax=1)
    ax.contour(xx,yy,zz,levels=[.5],colors="black",linewidths=1)
    xorx=np.array([[0,0],[0,1],[1,0],[1,1]])
    ax.scatter(xorx[:,0],xorx[:,1],c=np.array([0,1,1,0]),cmap="RdYlBu_r",
               s=90,edgecolors="black",vmin=0,vmax=1)
    ax.set(xlabel="x1",ylabel="x2",title="XOR: fronteira nao linear aprendida")
    fig.colorbar(im,ax=ax,label="P(y=1)")
    fig.tight_layout();fig.savefig(FIG/"xor.png");plt.close(fig)


def grafico_pertinencia(fuzzy):
    x=np.linspace(0,1,501);u=np.linspace(0,100,501)
    fig,axs=plt.subplots(1,3,figsize=(12,3.4))
    for ax,dom,fn,titulo in [
        (axs[0],x,fuzzy.conjuntos_entrada,"Risco de inadimplencia"),
        (axs[1],x,fuzzy.conjuntos_entrada,"Comprometimento de renda"),
        (axs[2],u,fuzzy.conjuntos_saida,"Limite (%)")]:
        for termo, y in fn(dom).items(): ax.plot(dom,y,label=termo.capitalize(),linewidth=2)
        ax.set(xlabel=titulo,ylabel="Pertinencia",ylim=(-.03,1.05))
        ax.legend(loc="upper center",fontsize=8,ncol=3)
    fig.tight_layout();fig.savefig(FIG/"pertinencias.png");plt.close(fig)


def grafico_superficie(fuzzy):
    eixos=np.linspace(0,1,51)
    z=np.array([[fuzzy.inferir(float(p),float(c)) for c in eixos] for p in eixos])
    fig,ax=plt.subplots(figsize=(7,5))
    im=ax.imshow(z,origin="lower",extent=[0,1,0,1],aspect="auto",cmap="viridis",vmin=0,vmax=100)
    ax.set(xlabel="Comprometimento de renda",ylabel="Probabilidade de inadimplencia",
           title="Superficie de controle Mamdani")
    fig.colorbar(im,ax=ax,label="Limite recomendado (% do maximo)")
    fig.tight_layout();fig.savefig(FIG/"superficie_fuzzy.png");plt.close(fig)


def grafico_ag(historico):
    fig,ax=plt.subplots(figsize=(8,3.7))
    x=[p["geracao"] for p in historico]
    ax.plot(x,[p["melhor"] for p in historico],marker="o",label="Melhor F1",linewidth=2)
    ax.plot(x,[p["media"] for p in historico],marker="s",label="F1 medio",linewidth=2)
    ax.set(xlabel="Geracao",ylabel="F1 de validacao",title="Convergencia do algoritmo genetico",
           xticks=x,ylim=(0,1))
    ax.legend();fig.tight_layout();fig.savefig(FIG/"convergencia_ag.png");plt.close(fig)


def grafico_comparativo(tabela):
    fig,ax=plt.subplots(figsize=(9,4))
    nomes=list(tabela)
    xx=np.arange(len(nomes));w=.2
    for j, met in enumerate(["acuracia","precisao","recall","f1"]):
        valores=[tabela[n][met] for n in nomes]
        barras=ax.bar(xx+(j-1.5)*w,valores,width=w,label=met.capitalize())
        # O valor impresso torna evidente que a figura foi montada com as
        # metricas desta execucao, e nao carregada como uma imagem ilustrativa.
        ax.bar_label(barras,labels=[f"{v:.2f}" for v in valores],padding=2,
                     fontsize=6,rotation=90)
    ax.set(xticks=xx,xticklabels=nomes,ylim=(0,1.08),ylabel="Valor",
           title="Desempenho comparado no teste (limiar 0,5)")
    ax.legend(ncol=4,fontsize=8,loc="upper center")
    fig.tight_layout();fig.savefig(FIG/"comparacao_modelos.png");plt.close(fig)

