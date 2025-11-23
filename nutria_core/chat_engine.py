import json
from typing import List, Tuple

from openai import OpenAI
from .tools_handler import handle_tool_calls
from .food_tools import tools


class ChatEngine:
    """
    Motor de conversación de NutrIA.

    - Recibe el mensaje del usuario y el historial (pares user/assistant).
    - Llama al modelo de OpenAI con las tools (function calling).
    - Si el modelo dispara tools, las ejecuta y hace una segunda llamada.
    - Devuelve una respuesta de texto lista para mostrar en la UI.
    """

    def __init__(
        self,
        api_key: str,
        model_llm: str,
        system_message: str,
        max_history: int = 6,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model_llm = model_llm
        self.system_message = system_message
        self.max_history = max_history  # limitar historial para rendimiento

    def _prepare_history(self, history: List[Tuple[str, str]]) -> List[dict]:
        """
        Convierte la lista de pares (usuario, asistente) en una
        lista de mensajes tipo OpenAI, manteniendo solo los últimos N.
        """
        compressed: List[dict] = []
        for u, a in history[-self.max_history:]:
            compressed.append({"role": "user", "content": u})
            compressed.append({"role": "assistant", "content": a})
        return compressed

    def chat(self, user_message: str, history: List[Tuple[str, str]]) -> str:
        """
        Flujo principal de conversación:

        1. Compactar historial
        2. Llamar al modelo con tools
        3. Si hay tool-calls → ejecutarlas
        4. Segunda llamada al modelo con resultados de tools
        5. Devolver la respuesta final en texto

        Maneja errores para no tumbar la app.
        """
        try:
            # 1) Historial compacto
            prepared = self._prepare_history(history)

            # 2) Construir mensajes
            messages: List[dict] = [
                {"role": "system", "content": self.system_message}
            ]
            messages.extend(prepared)
            messages.append({"role": "user", "content": user_message})

            # 3) Primera llamada al modelo
            response = self.client.chat.completions.create(
                model=self.model_llm,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            # 4) Si NO hay tool-calls → responder directo
            if not msg.tool_calls:
                return msg.content or "Lo siento, no pude generar una respuesta."

            # 5) Ejecutar tools
            tool_msgs = handle_tool_calls(msg.tool_calls, self.client)

            # 6) Añadir al contexto y segunda llamada
            messages.append(msg)
            messages.extend(tool_msgs)

            final = self.client.chat.completions.create(
                model=self.model_llm,
                messages=messages,
            )

            return final.choices[0].message.content or "No pude generar respuesta final."

        except Exception as e:
            # En producción no mostramos detalles, solo un mensaje amable
            return (
                "😔 Ocurrió un problema técnico al procesar tu solicitud. "
                "Intenta de nuevo en unos momentos o reformula tu mensaje."
            )
