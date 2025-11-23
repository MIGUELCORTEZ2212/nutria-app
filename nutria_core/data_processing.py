import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional

df = pd.read_csv("dataset_limpio.csv")

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
    candidatos = df[df["alimento"].str.contains(nombre, case=False, na=False)]
    return candidatos.iloc[0] if not candidatos.empty else None


def construir_foodinfo(fila):
    return FoodInfo(
        alimento=fila["alimento"],
        categoria=fila["categoria"],
        energia_kcal=float(fila["energia_kcal"]),
        proteina_g=float(fila["proteina_g"]),
        lipidos_g=float(fila["lipidos_g"]),
        hidratos_carbono_g=float(fila["hidratos_carbono_g"]),
        azucar_g=float(fila["azucar_g"]),
        sodio_g=float(fila["sodio_g"]),
        fibra_g=float(fila["fibra_g"]),
        medida=fila.get("medida"),
        cantidad=fila.get("cantidad")
    )


def calcular_nutria_score(fila):
    proteina = fila.get("proteina_g", 0) or 0
    fibra = fila.get("fibra_g", 0) or 0
    azucar = fila.get("azucar_g", 0) or 0
    sodio = fila.get("sodio_g", 0) or 0
    energia = fila.get("energia_kcal", 0) or 0
    carbs = fila.get("hidratos_carbono_g", 0) or 0
    lipidos = fila.get("lipidos_g", 0) or 0

    # COMPONENTES POSITIVOS
    score_proteina = min(proteina / 30, 1) * 30
    score_fibra = min(fibra / 10, 1) * 15
    score_carbs = max(0, 1 - (carbs / 60)) * 10  # carbos moderados = mejor puntuación

    # COMPONENTES NEGATIVOS
    score_azucar = max(0, 1 - (azucar / 20)) * 20
    score_sodio = max(0, 1 - (sodio / 800)) * 10
    score_kcal = max(0, 1 - (energia / 600)) * 10
    score_lipidos = max(0, 1 - (lipidos / 30)) * 15

    total = (
        score_proteina +
        score_fibra +
        score_carbs +
        score_azucar +
        score_sodio +
        score_kcal +
        score_lipidos
    )

    # Normalizar a 100
    return round((total / 110) * 100, 1)

def construir_foodinfo_score(fila):
    base = construir_foodinfo(fila)
    score = calcular_nutria_score(fila)
    return FoodInfoScore(**base.model_dump(), nutria_score=score)

