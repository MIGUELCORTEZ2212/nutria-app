import json

from .food_tools import get_food_info, get_nutrition_recommendations
from .nutritional_plan import DatosPaciente, generar_plan_nutricional


def handle_tool_calls(tool_calls, client):
    """
    Procesa las tool-calls enviadas por el modelo y devuelve una lista
    de mensajes con rol "tool" para ser agregados al contexto de OpenAI.

    Se añade manejo de errores para que una tool que falle no tumbe toda la conversación.
    """

    messages = []

    for call in tool_calls:
        name = call.function.name
        args_str = call.function.arguments or "{}"

        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            args = {}
        
        try:
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
                result = json.dumps(
                    {"error": f"Función desconocida: {name}"},
                    ensure_ascii=False,
                )

        except Exception as e:
            # Responder con error controlado a la tool
            result = json.dumps(
                {"error": f"Error interno en tool '{name}': {str(e)}"},
                ensure_ascii=False,
            )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": name,
                "content": result,
            }
        )

    return messages
