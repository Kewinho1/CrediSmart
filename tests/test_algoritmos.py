"""Testes de comportamento matemático, sem bibliotecas de ML proibidas.

Execute: python -m unittest discover -s tests -v
"""
import unittest

import numpy as np

from credismart.dados import gerar_dados, separar_padronizar
from credismart.modelos import MLP, PerceptronRosenblatt, metricas
from credismart.fuzzy import Mamdani
from credismart.genetico import AlgoritmoGenetico, Cromossomo
from credismart.relatorio_dados import extrair_integrantes


class TestDadosRelatorio(unittest.TestCase):
    def test_integrantes_sao_lidos_do_readme(self):
        conteudo = """# Projeto

## 1. Identificação do grupo

| Integrante | RA |
|---|---|
| Ana Silva | 123456 |
| Aluno(a) 2: Bruno Souza | 654321 |

## 2. Conteúdo
"""
        self.assertEqual(extrair_integrantes(conteudo), [
            {"nome": "Ana Silva", "ra": "123456"},
            {"nome": "Bruno Souza", "ra": "654321"},
        ])


class TestDados(unittest.TestCase):
    def test_dados_e_split_reproduziveis(self):
        X, y = gerar_dados()
        self.assertEqual(X.shape, (2000, 5))
        self.assertEqual(y.shape, (2000,))
        dados, classes, _, parametros = separar_padronizar()
        self.assertEqual([len(dados[k]) for k in ("treino", "validacao", "teste")], [1400, 300, 300])
        self.assertTrue(np.allclose(dados["treino"].mean(axis=0), 0, atol=1e-12))
        self.assertTrue(np.allclose(dados["treino"].std(axis=0), 1, atol=1e-12))
        self.assertEqual(sum(map(len, classes.values())), 2000)
        self.assertEqual(len(parametros["media"]), 5)

    def test_semente_altera_os_dados(self):
        x1, y1 = gerar_dados(seed=2026)
        x2, y2 = gerar_dados(seed=2027)
        self.assertFalse(np.array_equal(x1, x2))
        self.assertFalse(np.array_equal(y1, y2))


class TestMLP(unittest.TestCase):
    def test_xor_aprendido(self):
        x = np.array([[0.,0.], [0.,1.], [1.,0.], [1.,1.]])
        y = np.array([0, 1, 1, 0])
        rede = MLP(2, 8, taxa=.35, seed=29).fit(x, y, epocas=7500, lote=4, seed=29)
        np.testing.assert_array_equal(rede.predict(x), y)

    def test_gradiente_backprop_por_diferencas_finitas(self):
        rng = np.random.default_rng(12)
        x = rng.normal(size=(6, 3))
        y = np.array([0, 1, 0, 1, 1, 0], dtype=float).reshape(-1, 1)
        rede = MLP(3, 5, taxa=.1, seed=3)
        a1, _, pred = rede.forward(x)
        dz2 = (pred - y) / len(x)
        derivadas = {
            "W2": a1.T @ dz2,
            "b2": dz2.sum(axis=0, keepdims=True),
        }
        dz1 = (dz2 @ rede.W2.T) * (1 - a1*a1)
        derivadas["W1"] = x.T @ dz1
        derivadas["b1"] = dz1.sum(axis=0, keepdims=True)
        epsilon = 1e-5
        for nome, esperado in derivadas.items():
            peso = getattr(rede, nome)
            numerico = np.zeros_like(peso)
            for indice in np.ndindex(peso.shape):
                original = peso[indice]
                peso[indice] = original + epsilon
                loss_mais = rede.perda_logits(rede.forward(x)[1], y)
                peso[indice] = original - epsilon
                loss_menos = rede.perda_logits(rede.forward(x)[1], y)
                peso[indice] = original
                numerico[indice] = (loss_mais - loss_menos)/(2*epsilon)
            np.testing.assert_allclose(esperado, numerico, rtol=1e-4, atol=1e-6)

    def test_perceptron_nao_separa_xor(self):
        x = np.array([[0.,0.], [0.,1.], [1.,0.], [1.,1.]])
        y = np.array([0, 1, 1, 0])
        pred = PerceptronRosenblatt().fit(x, y).predict(x)
        self.assertLess(metricas(y, pred)["acuracia"], 1.)


class TestFuzzy(unittest.TestCase):
    def test_saida_valida_e_prioridade_do_risco(self):
        fuzzy = Mamdani()
        for risco in np.linspace(0,1,11):
            for comp in np.linspace(0,1,11):
                limite = fuzzy.inferir(risco, comp)
                self.assertGreaterEqual(limite, 0)
                self.assertLessEqual(limite, 100)
        self.assertGreater(fuzzy.inferir(.05,.05), fuzzy.inferir(.95,.95))

    def test_centroide_calculado(self):
        f = Mamdani()
        d = f.inferir(.3,.6,detalhar=True)
        self.assertEqual(len(d["regras"]), 9)
        self.assertAlmostEqual(d["centroide_percentual"], d["momento"]/d["area"],places=10)


class TestGenetico(unittest.TestCase):
    def test_reparo_cromossomo(self):
        self.assertEqual(AlgoritmoGenetico.reparar(Cromossomo(500,99.,1000)),
                         Cromossomo(32,.4,220))

    def test_dimensoes_minimas_obrigatorias(self):
        x=np.zeros((8,5)); y=np.zeros(8)
        with self.assertRaises(ValueError):
            AlgoritmoGenetico(x,y,x,y,populacao=9,geracoes=10)
        with self.assertRaises(ValueError):
            AlgoritmoGenetico(x,y,x,y,populacao=10,geracoes=9)


if __name__ == '__main__':
    unittest.main()
