from pydantic import BaseModel
from typing import Optional, List

class SchemeDoc(BaseModel):
    scheme_name: str
    summary: str
    eligibility: Optional[str] = None
    benefits: Optional[str] = None
    tags: List[str] = []
    state: Optional[str] = None
    official_link: Optional[str] = None
    source: str
