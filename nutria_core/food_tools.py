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

    # Filtrar por categoría si aplica
    if categoria and categoria.lower() != "todas":
        data = data[data["categoria"].str.lower() == categoria.lower()]

    # Excluir alimento base si aplica
    if alimento_base:
        data = data[~data["alimento"].str.contains(alimento_base, case=False)]

    # Orden por NutrIA score
    # Asegurar columnas antes de calcular score
    for col in ["proteina_g", "fibra_g", "azucar_g", "sodio_g", "energia_kcal", 
            "lipidos_g", "hidratos_carbono_g"]:
        if col not in data.columns:
            data[col] = 0
        data[col] = data[col].fillna(0)

    data["nutria_score"] = data.apply(lambda fila: calcular_nutria_score(fila), axis=1)
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
