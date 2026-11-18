"""MLP, backpropagation, Perceptron e métricas, sem bibliotecas de redes neurais."""
import math
import numpy as np

def sigmoide(x):
    z = np.clip(x, -40, 40)
    return 1.0 / (1.0 + np.exp(-z))


class MLP:
    """MLP com 1 camada oculta tanh, saida sigmoide, BCE e backprop.

    W1 (entradas, ocultas), b1 (ocultas,), W2 (ocultas,1), b2 (1,).
    O treinamento e feito por gradiente descendente em minibatches.
    """
    def __init__(self, n_entradas, n_ocultos=16, taxa=0.12, seed=2026):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, math.sqrt(1 / n_entradas), (n_entradas, n_ocultos))
        self.b1 = np.zeros((1, n_ocultos))
        self.W2 = rng.normal(0, math.sqrt(1 / n_ocultos), (n_ocultos, 1))
        self.b2 = np.zeros((1, 1))
        self.taxa = float(taxa)
        self.historico = {"treino":[], "validacao":[]}

    def forward(self, X):
        Z1 = X @ self.W1 + self.b1
        A1 = np.tanh(Z1)
        Z2 = A1 @ self.W2 + self.b2
        P = sigmoide(Z2)
        return A1, Z2, P

    @staticmethod
    def perda_logits(logits, y):
        """Binary cross entropy numericamente estavel usando logaddexp."""
        return float(np.mean(np.logaddexp(0, logits) - y * logits))

    def fit(self, X, y, epocas=140, lote=128, seed=2026, validacao=None):
        rng = np.random.default_rng(seed)
        y = np.asarray(y, dtype=float).reshape(-1, 1)
        n = len(X)
        for _ in range(int(epocas)):
            for idx in np.array_split(rng.permutation(n), math.ceil(n/lote)):
                xb, yb = X[idx], y[idx]
                m = len(idx)
                A1, Z2, P = self.forward(xb)
                # BCE+sigmoide: dL/dZ2 = (p - y)/m.
                dZ2 = (P-yb) / m
                dW2 = A1.T @ dZ2
                db2 = dZ2.sum(axis=0, keepdims=True)
                dZ1 = (dZ2 @ self.W2.T) * (1-A1*A1)
                dW1 = xb.T @ dZ1
                db1 = dZ1.sum(axis=0, keepdims=True)
                self.W1 -= self.taxa*dW1
                self.b1 -= self.taxa*db1
                self.W2 -= self.taxa*dW2
                self.b2 -= self.taxa*db2
            if validacao is not None:
                _, ztr, _ = self.forward(X)
                xv, yv = validacao
                _, zv, _ = self.forward(xv)
                self.historico["treino"].append(self.perda_logits(ztr, y))
                self.historico["validacao"].append(self.perda_logits(zv, np.asarray(yv).reshape(-1,1)))
        return self

    def predict_proba(self, X):
        return self.forward(X)[2].ravel()

    def predict(self, X, limiar=0.5):
        return (self.predict_proba(X) >= limiar).astype(int)


class PerceptronRosenblatt:
    """Classificador linear de Rosenblatt (pesos + vies), implementado do zero."""
    def __init__(self, taxa=0.03, epocas=60, seed=2026):
        self.taxa, self.epocas, self.seed = taxa, epocas, seed

    def fit(self, X, y):
        rng = np.random.default_rng(self.seed)
        self.pesos = np.zeros(X.shape[1])
        self.vies = 0.0
        for _ in range(self.epocas):
            for i in rng.permutation(len(y)):
                palpite = int(X[i] @ self.pesos + self.vies >= 0)
                erro = int(y[i]) - palpite
                self.pesos += self.taxa * erro * X[i]
                self.vies += self.taxa * erro
        return self

    def predict(self, X):
        return ((X @ self.pesos + self.vies) >= 0).astype(int)


def metricas(y, pred):
    y, pred = np.asarray(y).astype(int), np.asarray(pred).astype(int)
    tp = int(np.sum((y == 1) & (pred == 1)))
    fp = int(np.sum((y == 0) & (pred == 1)))
    tn = int(np.sum((y == 0) & (pred == 0)))
    fn = int(np.sum((y == 1) & (pred == 0)))
    prec = tp/(tp+fp) if tp+fp else 0.0
    rec = tp/(tp+fn) if tp+fn else 0.0
    f1 = 2*prec*rec/(prec+rec) if prec+rec else 0.0
    return {"acuracia":float((tp+tn)/len(y)), "precisao":float(prec),
            "recall":float(rec), "f1":float(f1),
            "TP":tp, "FP":fp, "TN":tn, "FN":fn}

