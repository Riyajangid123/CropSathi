from graph.state import AgroState
from nodes.llm import LLM


class LanguageNode:

    def __init__(self):
        self.llm = LLM().llm(reasoning_effort="none")

    def run(self, state: AgroState):
        question = state.get("question", "")

        if not question.strip():
            state["language"] = state.get("language", "English")
            return state

        prompt = f"""
Identify the language of the following text. Respond with ONLY the language
name in English (e.g. "Hindi", "English", "Marathi"), nothing else.

Text: {question}
"""
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        detected_language = response.content.strip()

        state["language"] = detected_language or "English"
        return state