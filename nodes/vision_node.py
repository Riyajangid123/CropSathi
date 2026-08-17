import json
import re

from graph.state import AgroState
from nodes.llm import LLM
from schemas.schema import VisionNodeSchema


class VisionNode:

    def __init__(self):
        self.llm = LLM().llm(reasoning_effort="none")   

    def run(self, state: AgroState):

        question = state.get("question", "")
        image = state.get("image", "")

        prompt = f"""
You are the vision analysis component of an agricultural AI system.

Analyze the uploaded plant image carefully.
Do not show your reasoning, analysis process, draft notes, or self-correction steps.
Output ONLY the final message to the farmer — no headers, no meta-commentary, no "Draft:" or "Analysis:" labels.

Farmer's question:
{question}

Your task is ONLY to analyze the image and produce structured observations.

Respond ONLY with a valid JSON object, and nothing else — no explanation, no markdown fences.
Use EXACTLY these keys:

{{
  "crop": "<string, the plant/crop if visually identifiable, else 'unknown'>",
  "disease": "<string, most likely disease/pest/abnormality if identifiable, else 'unknown'>",
  "observations": "<string, 2-4 concise sentences describing visible symptoms>",
  "confidence": <float between 0 and 1>,
  "needs_retrieval": <true or false>,
  "diagnosis_uncertain": <true or false>,
  "language": "<string, the language used by the farmer>"
}}

Important rules:
- Do not invent symptoms that are not visible.
- Do not claim certainty when the image is unclear.
- If multiple diseases are possible, mention the alternatives within the observations field.
- Do not provide treatment recommendations.
- If the image is unclear, use a low confidence score and set diagnosis_uncertain to true.
- confidence must be a number, and needs_retrieval / diagnosis_uncertain must be JSON booleans (true or false), not strings.
"""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image}},
                ],
            }
        ]

        raw_response = self.llm.invoke(messages)
        raw_text = raw_response.content

        parsed = self._extract_json(raw_text)
        validated = VisionNodeSchema(**parsed)


        state["crop"] = validated.crop
        state["disease"] = validated.disease
        state["observations"] = validated.observations
        state["language"] = validated.language
        state["confidence"] = validated.confidence
        state["needs_retrieval"] = validated.needs_retrieval
        state["diagnosis_uncertain"] = validated.diagnosis_uncertain

        return state

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Strip markdown fences if present, then parse JSON. Falls back to
        regex-extracting the first {...} block if the model added extra text."""
        cleaned = text.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.MULTILINE).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Could not parse JSON from model response: {text}")