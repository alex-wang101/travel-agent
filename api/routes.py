from fastapi import APIRouter, HTTPException
from api.models import QueryRequest, QueryResponse
from agents.init import inquiry_router
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Process the query using your existing agent
        response = inquiry_router.route_query(request.query)
        
        # Get the last memory entry to return context
        memory = inquiry_router.conversation_memory
        intent_type = memory.get("last_intent_type", "")
        flight_number = memory.get("last_flight_number")
        origin = memory.get("last_origin")
        destination = memory.get("last_destination")
        
        return QueryResponse(
            response=response,
            intent_type=intent_type,
            flight_number=flight_number,
            origin=origin,
            destination=destination
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))