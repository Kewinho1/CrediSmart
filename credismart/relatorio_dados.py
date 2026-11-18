"""Le metadados editaveis do relatorio a partir do README."""
from __future__ import annotations

import re
from pathlib import Path


def extrair_integrantes(texto_readme: str) -> list[dict[str, str]]:
    """Extrai os integrantes da primeira tabela de identificacao."""
    linhas = texto_readme.splitlines()
    na_secao = False
    na_tabela = False
    integrantes: list[dict[str, str]] = []

    for linha in linhas:
        texto = linha.strip()
        if texto.startswith("## "):
            if na_secao:
                break
            na_secao = "identifica" in texto.casefold() and "grupo" in texto.casefold()
            continue
        if not na_secao:
            continue
        if texto.startswith("|") and "integrante" in texto.casefold() and "ra" in texto.casefold():
            na_tabela = True
            continue
        if not na_tabela or not texto.startswith("|"):
            continue

        celulas = [item.strip() for item in texto.strip("|").split("|")]
        if len(celulas) < 2 or all(set(item) <= {"-", ":", " "} for item in celulas):
            continue
        nome = re.sub(r"^Aluno\(a\)(?:\s*\d+)?\s*:\s*", "", celulas[0], flags=re.IGNORECASE)
        integrantes.append({"nome": nome, "ra": celulas[1]})

    if not integrantes:
        raise ValueError("Tabela 'Identificacao do grupo' nao encontrada no README.md")
    return integrantes


def ler_integrantes(caminho: Path) -> list[dict[str, str]]:
    """Le o README e retorna os integrantes da tabela de identificacao."""
    return extrair_integrantes(caminho.read_text(encoding="utf-8"))

