import logging
from fastapi import APIRouter, HTTPException
from database.mission_db import MissionDB
from database.agent_db import AgentDB

router = APIRouter(prefix="/missions", tags=["missions"])
mission_db = MissionDB()
agent_db = AgentDB()
logger = logging.getLogger("app")

@router.post("", status_code=201)
def create_mission(data: dict):
    logger.info("POST /missions endpoint called")
    if not data or "title" not in data or "difficulty" not in data or "importance" not in data or "location" not in data:
        logger.error("Missing required mission fields")
        raise HTTPException(status_code=422, detail="Missing required fields")
        
    if not (1 <= data.get("difficulty", 0) <= 10) or not (1 <= data.get("importance", 0) <= 10):
        logger.error("Difficulty or importance out of bounds")
        raise HTTPException(status_code=400, detail="Invalid value range")
        
    logger.info("Executing SQL create mission")
    res = mission_db.create_mission(data)
    if not res.get("success"):
        logger.error(f"Failed to create mission: {res.get('message')}")
        raise HTTPException(status_code=400, detail=res.get("message"))
        
    logger.info(f"Mission created successfully with id: {res['data']['id']}")
    return {"message": "Mission Created", "data": res["data"]}

@router.get("")
def get_all_missions():
    logger.info("GET /missions endpoint called")
    logger.info("Fetching all missions from DB")
    missions = mission_db.get_all_missions()
    if missions is None:
        logger.error("Database connection failed")
        raise HTTPException(status_code=500, detail="Database error")
    logger.info("Successfully fetched missions list")
    return {"message": "Success", "data": missions}

@router.get("/{mission_id}")
def get_mission_by_id(mission_id: int):
    logger.info(f"GET /missions/{mission_id} endpoint called")
    logger.info("Searching for specific mission in DB")
    mission = mission_db.get_mission_by_id(mission_id)
    if not mission:
        logger.error(f"Mission {mission_id} not found")
        raise HTTPException(status_code=404, detail="Mission not found")
    logger.info(f"Successfully found mission {mission_id}")
    return {"message": "Success", "data": mission}

@router.put("/{mission_id}/assign/{agent_id}")
def assign_mission(mission_id: int, agent_id: int):
    logger.info(f"PUT /missions/{mission_id}/assign/{agent_id} called")
    logger.info("Validating assignment rules")
    
    mission = mission_db.get_mission_by_id(mission_id)
    if not mission:
        logger.error(f"Mission not found: {mission_id}")
        raise HTTPException(status_code=404, detail="Mission not found")
        
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent not found: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
        
    if mission["status"] != "NEW":
        logger.error("Mission status is not NEW")
        raise HTTPException(status_code=400, detail="Mission not available")
        
    if not agent["is_active"]:
        logger.error("Agent is inactive")
        raise HTTPException(status_code=400, detail="Agent is not active")
        
    open_missions = mission_db.get_open_missions_by_agent(agent_id)
    if len(open_missions) >= 3:
        logger.error("Agent reached maximum open missions")
        raise HTTPException(status_code=400, detail="Agent has reached maximum missions")
        
    if mission["risk_level"] == "CRITICAL" and agent["agent_rank"] != "Commander":
        logger.error("Non-commander assigned to critical mission")
        raise HTTPException(status_code=400, detail="Only Commander can handle critical missions")
        
    res = mission_db.assign_mission(mission_id, agent_id)
    logger.info("Successfully updated mission assignment")
    return {"message": "Success", "data": res.get("data")}

@router.put("/{mission_id}/start")
def start_mission(mission_id: int):
    logger.info(f"PUT /missions/{mission_id}/start called")
    mission = mission_db.get_mission_by_id(mission_id)
    if not mission:
        logger.error("Mission not found")
        raise HTTPException(status_code=404, detail="Mission not found")
        
    if mission["status"] != "ASSIGNED":
        logger.error("Mission status is not ASSIGNED")
        raise HTTPException(status_code=400, detail="Invalid mission status")
        
    logger.info("Updating status to IN_PROGRESS")
    res = mission_db.update_mission_status(mission_id, "IN_PROGRESS")
    logger.info(f"Mission {mission_id} started successfully")
    return {"message": "Success", "data": res.get("data")}

@router.put("/{mission_id}/complete")
def complete_mission(mission_id: int):
    logger.info(f"PUT /missions/{mission_id}/complete called")
    mission = mission_db.get_mission_by_id(mission_id)
    if not mission:
        logger.error("Mission not found")
        raise HTTPException(status_code=404, detail="Mission not found")
        
    if mission["status"] != "IN_PROGRESS":
        logger.error("Mission status is not IN_PROGRESS")
        raise HTTPException(status_code=400, detail="Invalid mission status")
        
    logger.info("Updating status to COMPLETED")
    res = mission_db.update_mission_status(mission_id, "COMPLETED")
    if mission.get("assigned_agent_id"):
        agent_db.increment_completed(mission["assigned_agent_id"])
    logger.info(f"Mission {mission_id} completed successfully")
    return {"message": "Success", "data": res.get("data")}

@router.put("/{mission_id}/fail")
def fail_mission(mission_id: int):
    logger.info(f"PUT /missions/{mission_id}/fail called")
    mission = mission_db.get_mission_by_id(mission_id)
    if not mission:
        logger.error("Mission not found")
        raise HTTPException(status_code=404, detail="Mission not found")
        
    if mission["status"] != "IN_PROGRESS":
        logger.error("Mission status is not IN_PROGRESS")
        raise HTTPException(status_code=400, detail="Invalid mission status")
        
    logger.info("Updating status to FAILED")
    res = mission_db.update_mission_status(mission_id, "FAILED")
    if mission.get("assigned_agent_id"):
        agent_db.increment_failed(mission["assigned_agent_id"])
    logger.info(f"Mission {mission_id} failed successfully")
    return {"message": "Success", "data": res.get("data")}

@router.put("/{mission_id}/cancel")
def cancel_mission(mission_id: int):
    logger.info(f"PUT /missions/{mission_id}/cancel called")
    mission = mission_db.get_mission_by_id(mission_id)
    if not mission:
        logger.error("Mission not found")
        raise HTTPException(status_code=404, detail="Mission not found")
        
    if mission["status"] not in ["NEW", "ASSIGNED"]:
        logger.error("Mission cannot be cancelled from this state")
        raise HTTPException(status_code=400, detail="Invalid mission status")
        
    logger.info("Updating status to CANCELLED")
    res = mission_db.update_mission_status(mission_id, "CANCELLED")
    logger.info(f"Mission {mission_id} cancelled successfully")
    return {"message": "Success", "data": res.get("data")}