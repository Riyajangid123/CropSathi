from graph.state import AgroState
from nodes.llm import LLM


class GenerateNode:

    def __init__(self):
        self.llm = LLM().llm(reasoning_format="hidden")

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

        docs_for_context = reranked_docs if reranked_docs else retrieved_docs

        if needs_retrieval and docs_for_context:
            knowledge_context = "\n\n".join(
                doc.get("content", str(doc)) if isinstance(doc, dict) else str(doc)
                for doc in docs_for_context
            )
        else:
            knowledge_context = "No additional retrieved knowledge available."

        prompt = f"""
You are AgroAssist, a friendly and knowledgeable agricultural assistant that talks directly with farmers to help them understand and treat plant health problems.

Always respond in the farmer's language: {language}

Farmer's message:
{question}

Image analysis findings (from the photo the farmer shared):
- Crop: {crop}
- Suspected disease/pest/abnormality: {disease}
- Visible symptoms: {observations}
- Diagnosis confidence: {confidence}
- Diagnosis marked uncertain: {diagnosis_uncertain}

Relevant agricultural knowledge retrieved for this case (treatment/management reference material):
{knowledge_context}

How to respond:

1. Talk like a helpful expert having a real conversation with the farmer — warm, respectful, and clear. Avoid robotic or overly formal language. No headers, no bullet-point walls unless it's genuinely a step-by-step treatment plan.
2. Briefly describe what was observed in the photo, in plain language (e.g. "the leaves show yellow spotting typical of..." rather than technical jargon).
3. If the retrieved knowledge above contains relevant treatment or management information, use it to give the farmer specific, actionable steps: what to apply or do, how much, how often, and any precautions. Base this strictly on the retrieved knowledge — do not invent product names, dosages, or timelines that aren't supported by it.
4. If the retrieved knowledge is thin, missing, or doesn't clearly match the diagnosis, say so honestly, give whatever safe general guidance you can (e.g. improving drainage, removing infected leaves, isolating affected plants), and recommend the farmer confirm with a local agricultural extension officer or expert before applying chemical treatments.
5. If diagnosis_uncertain is true or confidence is low, be upfront about the uncertainty in plain terms, and ask the farmer a clarifying question (e.g. how long they've noticed the symptoms, recent weather, whether other plants are affected) instead of guessing further.
6. End with a natural next step — a question, a check-in, or an offer to help further — the way a real advisor would, not a canned closing line.
7. Never mention internal system details like RAG, retrieval, confidence scores, node names, or "the documents provided" — just speak as yourself, the assistant.
8. Keep your response focused and complete — aim for roughly 150-250 words. Prioritize the most important, actionable information over exhaustive detail.

Now respond to the farmer.
"""

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        response = self.llm.invoke(messages)

        print("=" * 50)
        print("RAW RESPONSE CONTENT:", repr(response.content))
        print("RESPONSE ADDITIONAL KWARGS:", response.additional_kwargs)
        print("RESPONSE METADATA:", getattr(response, "response_metadata", None))
        print("=" * 50)

        state["context"] = knowledge_context
        state["answer"] = response.content

        return state

    