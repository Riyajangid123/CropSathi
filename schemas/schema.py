from pydantic import BaseModel, Field


class VisionNodeSchema(BaseModel):
    crop: str = Field(
        description="Identified plant or crop, or 'unknown' if not identifiable"
    )
    disease: str = Field(
        description="Most likely disease or pest, or 'unknown' if not identifiable"
    )
    observations: str = Field(
        description="2-4 concise sentences describing visible symptoms only"
    )
    language: str = Field(description="Language used by the farmer")
    confidence: float = Field(
        description="Confidence between 0 and 1",
        ge=0,
        le=1
    )
    needs_retrieval: bool = Field(
        description="Whether trusted agricultural knowledge should be retrieved"
    )
    diagnosis_uncertain: bool = Field(
        description="Whether the diagnosis is uncertain"
    )