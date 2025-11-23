import json
from .data_processing import (
    buscar_alimento_por_nombre,
    construir_foodinfo,
    construir_foodinfo_score,
    df
)
from .nutritional_plan import DatosPaciente, generar_plan_nutricional


# ======================================================
#  TOOL: get_food_info
# ======================================================

def get_food_info(nombre_alimento: str):
    fila = buscar_alimento_por_nombre(nombre_alimento)
    if fila is None:
        return json.dumps({"error": f"No encontré '{nombre_alimento}'"}, ensure_ascii=False)
    info = construir_foodinfo_score(fila)
    return info.model_dump_json(ensure_ascii=False)


# ======================================================
#  TOOL: get_nutrition_recommendations
# ======================================================

def get_nutrition_recommendations(objetivo, categoria=None, alimento_base=None, top_k=5):
    data = df.copy()

    # ---------------------------
    # 1. Normalización segura
    # ---------------------------
    objetivo = (objetivo or "").strip().lower()
    categoria = (categoria or "").strip().lower()
    alimento_base = (alimento_base or "").strip().lower()

    # ---------------------------
    # 2. Filtrar categoría SI existe y NO es "todas"
    # ---------------------------
    if categoria and categoria != "todas":
        data = data[data["categoria"].str.lower() == categoria]

    # ---------------------------
    # 3. Filtrar alimento base
    # NO FILTRAR si viene vacío o None
    # ---------------------------
    if alimento_base:
        data = data[~data["alimento"].str.lower().str.contains(alimento_base, na=False)]

    # Si luego de filtros no queda nada → fallback
    if data.empty:
        return json.dumps({
            "objetivo": objetivo,
            "alimento_base": alimento_base,
            "recomendaciones": [],
            "warning": "No se encontraron alimentos para recomendar."
        }, ensure_ascii=False)

    # ---------------------------
    # 4. Garantizar columnas
    # ---------------------------
    required = [
        "proteina_g", "fibra_g", "azucar_g", "sodio_g",
        "energia_kcal", "lipidos_g", "hidratos_carbono_g"
    ]
    for col in required:
        if col not in data.columns:
            data[col] = 0
        data[col] = data[col].fillna(0)

    # ---------------------------
    # 5. Cálculo robusto del score
    # ---------------------------
    data["nutria_score"] = data.apply(
        lambda fila: calcular_nutria_score(fila),
        axis=1
    )

    # ---------------------------
    # 6. Top K alimentos
    # ---------------------------
    top = data.sort_values("nutria_score", ascending=False).head(top_k)
    recomendaciones = [construir_foodinfo_score(row) for _, row in top.iterrows()]

    # ---------------------------
    # 7. Respuesta final
    # ---------------------------
    payload = {
        "objetivo": objetivo,
        "alimento_base": alimento_base,
        "recomendaciones": [rec.model_dump() for rec in recomendaciones]
    }

    return json.dumps(payload, ensure_ascii=False)


# ======================================================
#  DEFINICIÓN DE LAS TOOLS PARA OPENAI
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
                    "nombre_alimento": {"type": "string"}
                },
                "required": ["nombre_alimento"]
            }
        }
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
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": ["objetivo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_plan_nutricional",
            "description": "Genera un plan nutricional basado en TMB/TDEE.",
            "parameters": DatosPaciente.model_json_schema()
        }
    }
]
