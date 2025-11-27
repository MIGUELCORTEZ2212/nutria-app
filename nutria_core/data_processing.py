import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional

# =========================================================
# Carga de datos
# =========================================================

df = pd.read_csv("dataset_limpio.csv")

# Garantizamos que las columnas críticas existan y sean numéricas
NUMERIC_COLS = [
    "energia_kcal",
    "proteina_g",
    "lipidos_g",
    "hidratos_carbono_g",
    "azucar_g",
    "sodio_g",
    "fibra_g",
]

for col in NUMERIC_COLS:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# =========================================================
# Pydantic Models
# =========================================================

class FoodInfo(BaseModel):
    alimento: str
    categoria: str
    energia_kcal: float
    proteina_g: float
    lipidos_g: float
    hidratos_carbono_g: float
    azucar_g: float
    sodio_g: float
    fibra_g: float
    medida: Optional[str] = None
    cantidad: Optional[float] = None


class FoodInfoScore(FoodInfo):
    nutria_score: float = Field(..., description="Puntaje NutrIA de 0 a 100")


# =========================================================
# Helpers
# =========================================================

def buscar_alimento_por_nombre(nombre: str):
    """
    Busca el primer alimento cuyo nombre contenga el string dado (case-insensitive).
    Devuelve una fila (pd.Series) o None si no hay coincidencias.
    """
    candidatos = df[df["alimento"].str.contains(nombre, case=False, na=False)]
    return candidatos.iloc[0] if not candidatos.empty else None


def construir_foodinfo(fila) -> FoodInfo:
    """
    Construye un objeto FoodInfo a partir de una fila del DataFrame.
    """
    return FoodInfo(
        alimento=str(fila.get("alimento", "")),
        categoria=str(fila.get("categoria", "")),
        energia_kcal=float(fila.get("energia_kcal", 0) or 0),
        proteina_g=float(fila.get("proteina_g", 0) or 0),
        lipidos_g=float(fila.get("lipidos_g", 0) or 0),
        hidratos_carbono_g=float(fila.get("hidratos_carbono_g", 0) or 0),
        azucar_g=float(fila.get("azucar_g", 0) or 0),
        sodio_g=float(fila.get("sodio_g", 0) or 0),
        fibra_g=float(fila.get("fibra_g", 0) or 0),
        medida=fila.get("medida"),
        cantidad=float(fila.get("cantidad", 0) or 0)
        if "cantidad" in fila else None,
    )


def calcular_nutria_score(fila) -> float:
    """
    Calcula el NutrIA Score de forma robusta, protegiendo contra valores faltantes.

    Componentes:
    - Proteína (25%): positivo
    - Fibra (20%): positivo
    - Grasas totales (5%): se favorece menor grasa
    - Carbohidratos (5%): se favorece presencia moderada
    - Azúcar (20%): penalización
    - Sodio (15%): penalización
    - Energía kcal (10%): penalización por alta densidad
    """

    prot = float(fila.get("proteina_g", 0) or 0)
    fibra = float(fila.get("fibra_g", 0) or 0)
    azucar = float(fila.get("azucar_g", 0) or 0)
    sodio = float(fila.get("sodio_g", 0) or 0)
    kcal = float(fila.get("energia_kcal", 0) or 0)
    lipidos = float(fila.get("lipidos_g", 0) or 0)
    carbs = float(fila.get("hidratos_carbono_g", 0) or 0)

    # ---- Componentes positivos ----
    score = 0.0
    score += min(prot / 20.0, 1.0) * 25.0        # Proteína
    score += min(fibra / 7.0, 1.0) * 20.0       # Fibra
    score += max(0.0, (20.0 - lipidos) / 20.0) * 5.0  # Menos grasa es mejor
    score += min(carbs / 60.0, 1.0) * 5.0        # Carbohidratos "útiles"

    # ---- Penalizaciones (invertidos) ----
    score += max(0.0, 1.0 - (azucar / 35.0)) * 20.0   # Azúcar
    score += max(0.0, 1.0 - (sodio / 1500))* 15.0  # Sodio
    score += max(0.0, 1.0 - (kcal / 700.0)) * 10.0    # Kcal

     if kcal < 30:
     score += 20

    # Clamp a [0, 100]
    score = max(0.0, min(score, 100.0))
    return round(score, 1)


def construir_foodinfo_score(fila) -> FoodInfoScore:
    """
    Construye un FoodInfoScore (detalle del alimento + NutrIA Score).
    """
    base = construir_foodinfo(fila)
    score = calcular_nutria_score(fila)
    return FoodInfoScore(**base.model_dump(), nutria_score=score)
