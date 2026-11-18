"""Constantes e caminhos usados em todo o projeto."""
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figuras"
FIG.mkdir(exist_ok=True)
SEED = 2026
# Compatibilidade entre NumPy 1.x e 2.x
integral_trapezoidal = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
