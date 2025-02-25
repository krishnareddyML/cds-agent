from fastapi import APIRouter, Depends, HTTPException
from typing import List, AsyncGenerator

from fastapi.responses import StreamingResponse

from app.cds_agent_models import CdsAgentInput
from app.cds_agent_service import CdsAgentService


router = APIRouter(
    prefix="/cdsagent",
    tags=["CDSS", "Agent", "Clinical Decision Support System", "Falcon"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_root():
    return {"message": "Welcome to AGENTS FAST API!"}

@router.post("/run")
async def get_agent_response(agent_input: CdsAgentInput)->str:
    #print(agent_input)
    try:
        #print(conversation_input_model)
        agent_response = await CdsAgentService.run(agent_input)
        return agent_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))