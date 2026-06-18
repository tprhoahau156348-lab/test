import logging
from fastapi import APIRouter, HTTPException
from database.mission_db import MissionDB
from database.agent_db import AgentDB

router = APIRouter(prefix="/reports", tags=["reports"])
mission_db = MissionDB()
agent_db = AgentDB()
logger = logging.getLogger("app")

@router.get("/summary")
def get_summary():
    try:
        summary = {
            "active_agents_count": agent_db.count_active_agents(),
            "total_missions": mission_db.count_all_missions(),
            "open_missions": mission_db.count_open_missions(),
            "completed_missions": mission_db.count_by_status("COMPLETED"),
            "failed_missions": mission_db.count_by_status("FAILED")
        }
        logger.info("Summary report generated successfully")
        return {"message": "Succerss", "data": summary}
    except Exception as er:
        logger.error(f"Error creating summary report: {str(er)}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/missions-by-status")
def get_missions_by_status():
    try:
        report = {
            "open": mission_db.count_by_status("NEW") + mission_db.count_by_status("ASSIGNED"),
            "in_progress": mission_db.count_by_status("IN_PROGRESS"),
            "completed": mission_db.count_by_status("COMPLETED"),
            "failed": mission_db.count_by_status("FAILED"),
            "critical": mission_db.count_critical_missions()
        }
        logger.info("Status report generated successfully")
        return {"message": "Success", "data": report}
    except Exception as er:
        logger.error(f"Errorr creating status report: {str(er)}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/top-agent")
def get_top_agent():
    try:
        agent = mission_db.get_top_agent()
        if not agent:
            logger.error("No top agent found in database")
            raise HTTPException(status_code=404, detail="No top agent")
        logger.info("Top agent report fetched successfully")
        return {"message": "Success", "data": agent}
    except HTTPException as he:
        raise he
    except Exception as er:
        logger.error(f"Error fetching top agent: {str(er)}")
        raise HTTPException(status_code=500, detail="Database error")




