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
        azucar_g=float(fila["azucar_g"]),
        sodio_g=float(fila["sodio_g"]),
        fibra_g=float(fila["fibra_g"]),
        medida=fila.get("medida"),
        cantidad=fila.get("cantidad")
    )


def calcular_nutria_score(fila):
    score = 0
    score += min(fila["proteina_g"] / 30, 1) * 30
    score += min(fila["fibra_g"] / 10, 1) * 20
    score += max(0, 1 - (fila["azucar_g"] / 20)) * 25
    score += max(0, 1 - (fila["sodio_g"] / 800)) * 15
    score += max(0, 1 - (fila["energia_kcal"] / 600)) * 10
    return round(score, 1)


def construir_foodinfo_score(fila):
    base = construir_foodinfo(fila)
    score = calcular_nutria_score(fila)
    return FoodInfoScore(**base.model_dump(), nutria_score=score)

