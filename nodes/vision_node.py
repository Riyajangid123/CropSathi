import json
import re

from graph.state import AgroState
from nodes.llm import LLM
from schemas.schema import VisionNodeSchema


class VisionNode:

    def __init__(self):
        self.llm = LLM().llm(max_tokens=1500)

    def run(self, state: AgroState):

        question = state.get("question", "")
        image = state.get("image", "")

        prompt = f"""
You are an agricultural image analysis system.

Analyze the uploaded plant image.

Farmer's question:
{question}

Your job is ONLY to identify what is visibly present in the image.

Return ONLY one valid JSON object.

Do NOT:
- explain your reasoning
- show analysis steps
- use <think>
- provide treatment
- provide recommendations
- use markdown
- use ```json
- add text before or after the JSON

Use EXACTLY these keys:

{{
  "crop": "string",
  "disease": "string",
  "observations": "string",
  "confidence": 0.0,
  "needs_retrieval": true,
  "diagnosis_uncertain": true,
  "language": "string"
}}

Rules:

1. crop:
   Identify the crop if visually identifiable.
   Otherwise use "unknown".

2. disease:
   Identify the most likely disease, pest, or abnormality if visually identifiable.
   Otherwise use "unknown".

3. observations:
   Give only 1-2 concise sentences describing visible symptoms.
   Do not invent symptoms.

4. confidence:
   Must be a number between 0 and 1.

5. needs_retrieval:
   Set true if agricultural knowledge should be retrieved to verify the diagnosis.
   Otherwise false.

6. diagnosis_uncertain:
   Set true if the image is unclear or multiple diagnoses are possible.
   Otherwise false.

7. language:
   Use the language of the farmer's question.

Return JSON only.
"""

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image
                        }
                    }
                ]
            }
        ]

        raw_response = self.llm.invoke(messages)

        print("\n===== VISION RESPONSE =====")
        print("CONTENT:", repr(raw_response.content))
        print("ADDITIONAL KWARGS:", raw_response.additional_kwargs)
        print("RESPONSE METADATA:", raw_response.response_metadata)
        print("===========================\n")

        raw_text = raw_response.content

        if not raw_text or not raw_text.strip():

            raise ValueError(
                "Vision model returned empty content. "
                "Check reasoning configuration/output token limit."
            )

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

        if not text or not text.strip():
            raise ValueError(
                "Model returned empty content."
            )

        cleaned = text.strip()

        # Remove <think>...</think> if the model happens to include it
        cleaned = re.sub(
            r"<think>.*?</think>",
            "",
            cleaned,
            flags=re.DOTALL | re.IGNORECASE
        ).strip()

        # Remove markdown fences
        cleaned = re.sub(
            r"```(?:json)?",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = cleaned.replace("```", "").strip()

        # First try parsing the entire response
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # If extra text exists, find the JSON object
        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                f"Could not find JSON in model response:\n{cleaned}"
            )

        json_text = match.group(0)

        try:
            return json.loads(json_text)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON from model response:\n{json_text}"
            ) from e