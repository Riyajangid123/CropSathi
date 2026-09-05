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

Answering completeness:

The farmer's message may contain more than one question or request in the same
sentence (for example, asking about the weather AND whether it's safe to spray,
or asking for a diagnosis AND how urgent it is). Before responding, identify
every distinct question or request in the farmer's message, and make sure your
final reply addresses each one individually — do not answer only the first or
easiest part and skip the rest.

If you called a tool (such as weather lookup) to get information, do not just
report the raw data back to the farmer. Always connect that data directly to
what they actually asked:
- If they asked whether it's safe to spray, fertilize, irrigate, or do field
  work, explicitly say whether current conditions are favorable or
  unfavorable for that specific activity, and briefly explain why (e.g. high
  humidity or expected rain can wash off spray or reduce effectiveness; strong
  wind can cause drift; extreme heat can stress the crop during application).
- If they asked about disease risk, connect humidity/rainfall/temperature to
  whether conditions currently favor disease spread for their crop.
- Never leave a raw number (temperature, humidity, wind speed) sitting on its
  own without a clear "so here's what that means for you" statement.

Before finalizing your response, mentally check: did I answer every part of
what the farmer actually asked? If not, revise your answer to cover the
missing part before responding.

Important:
- Do not invent treatment dosages.
- Use retrieved agricultural knowledge for specific treatment recommendations.
- If diagnosis is uncertain, clearly communicate that uncertainty.
- Do not mention RAG, retrieval, nodes, tools, confidence scores,
  or internal system details.

Respond naturally and helpfully to the farmer.
"""

        messages = state.get("messages", [])

        if not messages:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        else:
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