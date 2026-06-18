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
