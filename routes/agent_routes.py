import logging
from fastapi import APIRouter, HTTPException
from database.agent_db import AgentDB

router = APIRouter(prefix="/agents", tags=["agents"])
agent_db = AgentDB()
logger = logging.getLogger("app")

@router.post("", status_code=201)
def create_agent(data: dict):
    logger.info("POST /agents endpoint called")
    if not data or "name" not in data or "agent_rank" not in data or "specialty" not in data:
        logger.error("Missing fields or empty body")
        raise HTTPException(status_code=422, detail="Missing required fields")
    
    if data.get("agent_rank") not in ["Junior", "Senior", "Commander"]:
        logger.error("Invalid agent rank provided")
        raise HTTPException(status_code=400, detail="Invalid agent rank")
        
    res = agent_db.create_agent(data)
    if not res.get("success"):
        logger.error(f"Database error during creation: {res.get('message')}")
        raise HTTPException(status_code=400, detail=res.get("message"))
        
    logger.info(f"Agent created successfully with id: {res['data']['id']}")
    print ("Successfully completed")
    return {"message": "Agent Created", "data": res["data"]}

@router.get("")
def get_all_agents():
    logger.info("GET /agents endpoint called")
    agents = agent_db.get_all_agents()
    if agents is None:
        logger.error("Failed to get agents from database")
        raise HTTPException(status_code=500, detail="Database error")
    logger.info("Successfully fetched all agents list")
    print ("Successfully completed")
    return {"message": "Success", "data": agents}

@router.get("/{agent_id}")
def get_agent_by_id(agent_id: int):
    logger.info(f"GET /agents/{agent_id} endpoint called")
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent with id {agent_id} not found")
        raise HTTPException(status_code=404, detail="Agent not found")
    logger.info(f"Successfully found agent {agent_id}")
    print ("Successfully completed")
    return {"message": "Success", "data": agent}

@router.get("/{agent_id}/performance")
def get_agent_performance(agent_id: int):
    logger.info(f"GET /agents/{agent_id}/performance endpoint called")
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent {agent_id} not found for performance check")
        raise HTTPException(status_code=404, detail="Agent not found")
    perf = agent_db.get_agent_performance(agent_id)
    logger.info(f"Successfully generated performance for agent {agent_id}")
    print ("Successfully completed")
    return {"message": "Success", "data": perf}

@router.put("/{agent_id}")
def update_agent(agent_id: int, data: dict):
    logger.info(f"PUT /agents/{agent_id} endpoint called")
    if not data:
        logger.error("Empty body received for update")
        raise HTTPException(status_code=400, detail="Empty body")
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent {agent_id} not found for update")
        raise HTTPException(status_code=404, detail="Agent not found")
    res = agent_db.update_agent(agent_id, data)
    logger.info(f"Agent {agent_id} updated successfully")
    print ("Successfully completed")
    return {"message": "Success", "data": res.get("data")}

@router.put("/{agent_id}/deactivate")
def deactivate_agent(agent_id: int):
    logger.info(f"PUT /agents/{agent_id}/deactivate endpoint called")
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent {agent_id} not found for deactivation")
        raise HTTPException(status_code=404, detail="Agent not found")
    res = agent_db.deactivate_agent(agent_id)
    logger.info(f"Agent {agent_id} deactivated successfully")
    print ("Successfully completed")
    return {"message": "Success", "data": res.get("data")}