from pydantic import BaseModel

class UserMessage(BaseModel):
    message: str

class IntentAnalysisResponse(BaseModel):
    intent_summary: str
    extracted_details: dict
    clarity: str
    missing_information: list
