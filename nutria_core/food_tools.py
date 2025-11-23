import json
import pandas as pd

from .data_processing import (
    df,
    buscar_alimento_por_nombre,
    construir_foodinfo,
    construir_foodinfo_score,
    calcular_nutria_score,
)
from .nutritional_plan import DatosPaciente, generar_plan_nutricional


# ======================================================
#  TOOL: get_food_info
# ======================================================

def get_food_info(nombre_alimento: str):
    """
    Devuelve información nutricional + NutrIA Score de un alimento.
    """
    fila = buscar_alimento_por_nombre(nombre_alimento)
    if fila is None:
        return json.dumps(
            {"error": f"No encontré '{nombre_alimento}' en el dataset."},
            ensure_ascii=False,
        )

    info = construir_foodinfo_score(fila)
    return info.model_dump_json(ensure_ascii=False)


# ======================================================
#  TOOL: get_nutrition_recommendations
# ======================================================

def get_nutrition_recommendations(
    objetivo: str,
    categoria: str = None,
    alimento_base: str = None,
    top_k: int = 5,
):
    """
    Recomienda alimentos usando NutrIA Score.
    Incluye protección ante errores del usuario y del modelo.
    """

    # ------------------------------------------------------
    # 0) Blindaje absoluto: normalizar y evitar valores None
    # ------------------------------------------------------
    objetivo = (objetivo or "").strip().lower()
    categoria = (categoria or "").strip().lower()
    alimento_base = (alimento_base or "").strip().lower()

    # Si NO hay objetivo → default seguro
    if objetivo == "":
        objetivo = "mejorar alimentación general"

    data = df.copy()

    # ------------------------------------------------------
    # 1) Filtrar por categoría (solo si realmente existe)
    # ------------------------------------------------------
    if categoria and categoria != "todas":
        data = data[data["categoria"].str.lower() == categoria]

    # ------------------------------------------------------
    # 2) Filtrar alimento base (solo si no viene vacío)
    # ------------------------------------------------------
    if alimento_base:
        data = data[~data["alimento"].str.lower().str.contains(alimento_base, na=False)]

    # ------------------------------------------------------
    # 3) Si ya no queda nada, responder limpio
    # ------------------------------------------------------
    if data.empty:
        return json.dumps(
            {
                "objetivo": objetivo,
                "alimento_base": alimento_base,
                "recomendaciones": [],
                "warning": "No se encontraron alimentos para recomendar con esos filtros.",
            },
            ensure_ascii=False,
        )

    # ------------------------------------------------------
    # 4) Garantizar todas las columnas del score
    # ------------------------------------------------------
    required = [
        "proteina_g",
        "fibra_g",
        "azucar_g",
        "sodio_g",
        "energia_kcal",
        "lipidos_g",
        "hidratos_carbono_g",
    ]

    for col in required:
        if col not in data.columns:
            data[col] = 0
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    # ------------------------------------------------------
    # 5) Cálculo del NutrIA Score (a prueba de todo)
    # ------------------------------------------------------
    try:
        data["nutria_score"] = data.apply(
            lambda fila: calcular_nutria_score(fila),
            axis=1,
        )
    except Exception as e:
        # FALLBACK PARA QUE NUNCA TRUENE LA APP
        return json.dumps(
            {
                "objetivo": objetivo,
                "alimento_base": alimento_base,
                "error": f"No se pudo calcular el NutrIA Score: {str(e)}",
                "recomendaciones": [],
            },
            ensure_ascii=False,
        )

    # ------------------------------------------------------
    # 6) Tomar top K alimentos
    # ------------------------------------------------------
    data = data.sort_values("nutria_score", ascending=False)
    top = data.head(top_k)

    recomendaciones = []
    for _, row in top.iterrows():
        try:
            recomendaciones.append(construir_foodinfo_score(row).model_dump())
        except Exception:
            continue

    # Último check para evitar listas vacías
    if not recomendaciones:
        return json.dumps(
            {
                "objetivo": objetivo,
                "alimento_base": alimento_base,
                "recomendaciones": [],
                "warning": "No se pudieron construir las recomendaciones.",
            },
            ensure_ascii=False,
        )

    # ------------------------------------------------------
    # 7) Respuesta final robusta
    # ------------------------------------------------------
    return json.dumps(
        {
            "objetivo": objetivo,
            "alimento_base": alimento_base,
            "recomendaciones": recomendaciones,
        },
        ensure_ascii=False,
    )


# ======================================================
#  DEFINICIÓN DE TOOLS
# ======================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_food_info",
            "description": "Obtiene información nutricional de un alimento desde el dataset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_alimento": {"type": "string"},
                },
                "required": ["nombre_alimento"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nutrition_recommendations",
            "description": "Recomienda alimentos según un objetivo nutricional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "objetivo": {"type": "string"},
                    "categoria": {"type": "string", "nullable": True},
                    "alimento_base": {"type": "string", "nullable": True},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["objetivo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generar_plan_nutricional",
            "description": "Genera un plan nutricional basado en TMB y TDEE.",
            "parameters": DatosPaciente.model_json_schema(),
        },
    },
]
