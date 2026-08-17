from langchain_groq import ChatGroq


class LLM:
    def llm(self, reasoning_effort: str = None, reasoning_format: str = None, max_tokens: int = 3072):
        kwargs = {}
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
        if reasoning_format:
            kwargs["reasoning_format"] = reasoning_format

        return ChatGroq(
            model="qwen/qwen3.6-27b",
            max_tokens=max_tokens,
            temperature=0.7,
            **kwargs,
        )