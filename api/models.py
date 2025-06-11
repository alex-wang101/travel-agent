from pydantic import BaseModel
from typing import Optional 

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    intent_type: Optional[str] = None
    flight_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None