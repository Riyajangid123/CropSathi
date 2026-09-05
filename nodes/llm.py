from langchain_groq import ChatGroq


class LLM:

    def llm(self, max_tokens: int = 800):

        return ChatGroq(
            model="qwen/qwen3.6-27b",
            max_tokens=max_tokens,
            temperature=0,
            reasoning_effort="none"
        )