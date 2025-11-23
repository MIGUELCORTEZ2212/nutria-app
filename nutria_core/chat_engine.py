import json
from openai import OpenAI
from .tools_handler import handle_tool_calls
from .food_tools import tools

class ChatEngine:

    def __init__(self, api_key, model_llm, system_message, max_history=6):
        self.client = OpenAI(api_key=api_key)
        self.model_llm = model_llm
        self.system_message = system_message
        self.max_history = max_history  # limitar historial

    def _prepare_history(self, history):
        """
        Mantiene solo los últimos N turnos para acelerar la respuesta.
        """
        compressed = []
        for u, a in history[-self.max_history :]:
            compressed.append({"role": "user", "content": u})
            compressed.append({"role": "assistant", "content": a})
        return compressed

    def chat(self, user_message, history):
        """
        Flujo optimizado:
        1. Prepara un historial compacto (últimos N turns)
        2. Primera llamada al modelo
        3. Si hay tools → ejecutarlas y hacer segunda llamada
        4. Devuelve respuesta final
        """

        # Compactar historial
        prepared = self._prepare_history(history)

        # Construir prompt
        messages = [{"role": "system", "content": self.system_message}]
        messages.extend(prepared)
        messages.append({"role": "user", "content": user_message})

        # PRIMERA LLAMADA
        response = self.client.chat.completions.create(
            model=self.model_llm,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        # Si NO hay tool-calls → devolver directamente
        if not msg.tool_calls:
            return msg.content

        # Ejecutar las tools
        tool_msgs = handle_tool_calls(msg.tool_calls, self.client)

        # Añadir tool-calls al mensaje final
        messages.append(msg)
        messages.extend(tool_msgs)

        # SEGUNDA LLAMADA — respuesta final
        final = self.client.chat.completions.create(
            model=self.model_llm,
            messages=messages
        )

        return final.choices[0].message.content
