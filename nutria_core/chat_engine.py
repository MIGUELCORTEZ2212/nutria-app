import json
from openai import OpenAI
from .tools_handler import handle_tool_calls
from .food_tools import tools

class ChatEngine:

    def __init__(self, api_key, model_llm, system_message):
        self.client = OpenAI(api_key=api_key)
        self.model_llm = model_llm
        self.system_message = system_message

    def chat(self, user_message, history):
        """Orquesta el diálogo entre usuario y el modelo + tool-calls."""
        messages = [{"role": "system", "content": self.system_message}]

        for u, a in history:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})

        messages.append({"role": "user", "content": user_message})

        # primera llamada
        response = self.client.chat.completions.create(
            model=self.model_llm,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_msg = response.choices[0].message

        # si no hay tool-calls
        if not assistant_msg.tool_calls:
            return assistant_msg.content

        # si sí hay tools
        tool_messages = handle_tool_calls(assistant_msg.tool_calls, self.client)
        messages.append(assistant_msg)
        messages.extend(tool_messages)

        # llamada final
        final = self.client.chat.completions.create(
            model=self.model_llm,
            messages=messages
        )

        return final.choices[0].message.content
