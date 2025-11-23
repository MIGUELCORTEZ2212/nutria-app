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
    # Extraer valores del alimento
    prot = fila["proteina_g"]
    fib = fila["fibra_g"]
    carbs = fila["hidratos_carbono_g"]
    azu = fila["azucar_g"]
    sod = fila["sodio_g"]
    lip = fila["lipidos_g"]
    kcal = fila["energia_kcal"]

    # Percentiles positivos
    p_prot = df["proteina_g"].rank(pct=True).iloc[fila.name]
    p_fib = df["fibra_g"].rank(pct=True).iloc[fila.name]
    
    # Carbohidratos útiles: se premian valores moderados (no extremos)
    # Fórmula: más cerca de la mediana = mejor
    carbs_mediana = df["hidratos_carbono_g"].median()
    p_carbs = max(0, 1 - abs(carbs - carbs_mediana) / (df["hidratos_carbono_g"].max() + 1))

    # Percentiles negativos (inversos)
    p_azu = 1 - df["azucar_g"].rank(pct=True).iloc[fila.name]
    p_sod = 1 - df["sodio_g"].rank(pct=True).iloc[fila.name]
    p_lip = 1 - df["lipidos_g"].rank(pct=True).iloc[fila.name]
    p_kcal = 1 - df["energia_kcal"].rank(pct=True).iloc[fila.name]

    # Ponderaciones (suman 100)
    score = (
        p_prot * 25 +
        p_fib * 20 +
        p_carbs * 10 +
        p_azu * 20 +
        p_sod * 10 +
        p_lip * 10 +
        p_kcal * 5
    )

    return round(score, 1)

    # Normalizar a 100
    return round((total / 110) * 100, 1)

def construir_foodinfo_score(fila):
    base = construir_foodinfo(fila)
    score = calcular_nutria_score(fila)
    return FoodInfoScore(**base.model_dump(), nutria_score=score)

