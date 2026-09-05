from graph.state import AgroState
from nodes.llm import LLM
from tools.weather_api import get_coordinates, get_weather


class GenerateNode:

    def __init__(self):
        self.llm = LLM().llm()

        self.tools = [
            get_coordinates,
            get_weather
        ]

        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def run(self, state: AgroState):

        question = state.get("question", "")
        crop = state.get("crop", "Unknown")
        disease = state.get("disease", "Unknown")
        observations = state.get("observations", "")
        confidence = state.get("confidence", 0.0)
        language = state.get("language", "English")
        needs_retrieval = state.get("needs_retrieval", False)
        diagnosis_uncertain = state.get("diagnosis_uncertain", False)

        retrieved_docs = state.get("retrieved_docs", [])
        reranked_docs = state.get("reranked_docs", [])

        docs_for_context = (
            reranked_docs
            if reranked_docs
            else retrieved_docs
        )

        if needs_retrieval and docs_for_context:

            knowledge_context = "\n\n".join(
                doc.get("content", str(doc))
                if isinstance(doc, dict)
                else str(doc)
                for doc in docs_for_context
            )

        else:
            knowledge_context = (
                "No additional retrieved knowledge available."
            )

        prompt = f"""
You are AgroAssist, a friendly and knowledgeable agricultural assistant.

Always respond in the farmer's language: {language}

Farmer's message:
{question}

Image analysis findings:
- Crop: {crop}
- Suspected disease/pest/abnormality: {disease}
- Visible symptoms: {observations}
- Diagnosis confidence: {confidence}
- Diagnosis uncertain: {diagnosis_uncertain}

Relevant agricultural knowledge:
{knowledge_context}

Weather/location tools:

If the farmer provides a location or asks about weather:

1. Use get_coordinates to convert the farmer's location name
   into latitude and longitude.

2. Then use get_weather with those coordinates.

3. Use the weather information when relevant to:
   - irrigation
   - disease risk
   - rainfall
   - spraying conditions
   - crop health
   - agricultural recommendations

The farmer should NEVER need to provide latitude and longitude manually.

If weather information is not relevant, do not call the weather tools.

Important:
- Do not invent treatment dosages.
- Use retrieved agricultural knowledge for specific treatment recommendations.
- If diagnosis is uncertain, clearly communicate that uncertainty.
- Do not mention RAG, retrieval, nodes, tools, confidence scores,
  or internal system details.

Respond naturally and helpfully to the farmer.
"""

        # Existing conversation/tool messages
        messages = state.get("messages", [])

        # First generation
        if not messages:

            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        else:

            # Add updated agricultural context if needed
            messages = messages

        response = self.llm_with_tools.invoke(messages)

        print("=" * 50)
        print("RAW RESPONSE:", repr(response.content))
        print("TOOL CALLS:", getattr(response, "tool_calls", None))
        print("=" * 50)

        return {
            "messages": [response],
            "context": knowledge_context,
            "answer": response.content
        }