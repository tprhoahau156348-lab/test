import logging
from fastapi import FastAPI
from database.db_connection import DB_Connection
from routes.agent_routes import router as agent_router
from routes.mission_routes import router as mission_router
from routes.report_routes import router as report_router

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

db = DB_Connection()
db.create_database()
db.create_tables()

app = FastAPI()

app.include_router(agent_router)
app.include_router(mission_router)
app.include_router(report_router)