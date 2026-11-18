"""Constantes e caminhos usados em todo o projeto."""
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
import numpy as np

BASE = Path(__file__).resolve().parent.parent
# Cada execução recebe um diretório novo. O relatório passa a apontar para os
# gráficos da execução atual em vez de depender de PNGs antigos do pacote.
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ") + "_" + uuid4().hex[:6]
FIG = BASE / "figuras" / f"execucao_{RUN_ID}"
FIG.mkdir(parents=True, exist_ok=True)
SEED = 2026
# Compatibilidade entre NumPy 1.x e 2.x
integral_trapezoidal = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
