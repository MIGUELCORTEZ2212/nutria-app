import json
from .food_tools import get_food_info, get_nutrition_recommendations, tools
from .nutritional_plan import DatosPaciente, generar_plan_nutricional

def handle_tool_calls(tool_calls, client):
    """
    Procesa las tool-calls enviadas por el modelo y devuelve mensajes
    que Streamlit + OpenAI pueden interpretar correctamente.
    """

    messages = []

    for call in tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments or "{}")

        # ---------------------------
        # Tool: get_food_info
        # ---------------------------
        if name == "get_food_info":
            result = get_food_info(**args)

        # ---------------------------
        # Tool: get_nutrition_recommendations
        # ---------------------------
        elif name == "get_nutrition_recommendations":
            result = get_nutrition_recommendations(**args)

        # ---------------------------
        # Tool: generar_plan_nutricional
        # ---------------------------
        elif name == "generar_plan_nutricional":
            datos = DatosPaciente(**args)
            plan = generar_plan_nutricional(datos)
            result = plan.model_dump_json(ensure_ascii=False)

        else:
            result = json.dumps({"error": f"Función desconocida: {name}"})

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": name,
            "content": result
        })

    return messages
