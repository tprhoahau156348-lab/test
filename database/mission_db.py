import mysql.connector
from mysql.connector import Error
from .db_connection import DB_Connection

class MissionDB:
    
    VALID_STATUSES = ['NEW', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED']
    
    def __init__(self):
        self.db = DB_Connection()
    
    def calculate_risk_level(self, difficulty, importance):
        total_score = difficulty * 2
        total_score = total_score + importance
        
        if total_score <= 9:
            risk = "LOW"
        elif total_score <= 17:
            risk = "MEDIUM"
        elif total_score <= 24:
            risk = "HIGH"
        else:
            risk = "CRITICAL"
        
        return risk
    
    def create_mission(self, data):
        try:
            difficulty = data.get('difficulty')
            importance = data.get('importance')
            
            if not isinstance(difficulty, int) or not (1 <= difficulty <= 10):
                return {"success": False, "message": "Difficulty must be an integer between 1 and 10"}
            if not isinstance(importance, int) or not (1 <= importance <= 10):
                return {"success": False, "message": "Importance must be an integer between 1 and 10"}
            
            risk_level = self.calculate_risk_level(difficulty, importance)
            
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                query = "INSERT INTO missions (title, description, location, difficulty, importance, status, risk_level, assigned_agent_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                title = data.get('title')
                description = data.get('description')
                location = data.get('location')
                
                values = (title, description, location, difficulty, importance, 'NEW', risk_level, None)
                cursor.execute(query, values)
                conn.commit()
                mission_id = cursor.lastrowid
            
            conn.close()
            mission = self.get_mission_by_id(mission_id)
            return {"success": True, "data": mission}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def get_all_missions(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM missions")
                missions = cursor.fetchall()
            
            conn.close()
            if missions:
                return missions
            else:
                return []
        except Error as e:
            print(f"Error: {e}")
            return []
    
    def get_mission_by_id(self, mission_id):
        try:
            conn = self.db.get_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM missions WHERE id = %s", (mission_id,))
                mission = cursor.fetchone()
            
            conn.close()
            if mission:
                return mission
            else:
                return None
        except Error as e:
            print(f"Error: {e}")
            return None
    
    def assign_mission(self, mission_id, agent_id):
        try:
            from .agent_db import AgentDB
            agent_db = AgentDB()
            
            mission = self.get_mission_by_id(mission_id)
            if not mission:
                return {"success": False, "message": "Mission not found"}
            
            status = mission['status']
            if status != 'NEW':
                return {"success": False, "message": "Can only assign missions with status NEW"}
            
            agent = agent_db.get_agent_by_id(agent_id)
            if not agent:
                return {"success": False, "message": "Agent not found"}
            
            agent_active = agent['is_active']
            if not agent_active:
                return {"success": False, "message": "Cannot assign mission to inactive agent"}
            
            open_missions = self.get_open_missions_by_agent(agent_id)
            open_count = len(open_missions)
            if open_count >= 3:
                return {"success": False, "message": "Agent already has 3 open missions"}
            
            risk = mission['risk_level']
            rank = agent['agent_rank']
            if risk == 'CRITICAL':
                if rank != 'Commander':
                    return {"success": False, "message": "Only Commanders can be assigned CRITICAL missions"}
            
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                cursor.execute("UPDATE missions SET assigned_agent_id = %s, status = 'ASSIGNED' WHERE id = %s", (agent_id, mission_id))
                conn.commit()
            
            conn.close()
            return {"success": True, "message": "Mission assigned successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def update_mission_status(self, mission_id, status):
        try:
            status_valid = status in self.VALID_STATUSES
            if not status_valid:
                return {"success": False, "message": f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}"}
            
            mission = self.get_mission_by_id(mission_id)
            if not mission:
                return {"success": False, "message": "Mission not found"}
            
            current_status = mission['status']
            
            can_start = (status == 'IN_PROGRESS' and current_status != 'ASSIGNED')
            if can_start:
                return {"success": False, "message": "Can only start missions with status ASSIGNED"}
            
            can_complete = (status == 'COMPLETED' and current_status != 'IN_PROGRESS')
            if can_complete:
                return {"success": False, "message": "Can only complete/fail missions with status IN_PROGRESS"}
            
            can_fail = (status == 'FAILED' and current_status != 'IN_PROGRESS')
            if can_fail:
                return {"success": False, "message": "Can only complete/fail missions with status IN_PROGRESS"}
            
            can_cancel = (status == 'CANCELLED')
            if can_cancel:
                if current_status != 'NEW' and current_status != 'ASSIGNED':
                    return {"success": False, "message": "Can only cancel missions with status NEW or ASSIGNED"}
            
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                cursor.execute("UPDATE missions SET status = %s WHERE id = %s", (status, mission_id))
                conn.commit()
            
            conn.close()
            return {"success": True, "message": "Mission status updated successfully"}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def get_open_missions_by_agent(self, agent_id):
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM missions WHERE assigned_agent_id = %s AND status IN ('ASSIGNED', 'IN_PROGRESS')", (agent_id,))
                missions = cursor.fetchall()
            
            conn.close()
            if missions:
                return missions
            else:
                return []
        except Error as e:
            print(f"Error: {e}")
            return []
    
    def count_all_missions(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return 0
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM missions")
                result = cursor.fetchone()
            
            conn.close()
            count = result[0]
            return count
        except Error as e:
            print(f"Error: {e}")
            return 0
    
    def count_by_status(self, status):
        try:
            conn = self.db.get_connection()
            if not conn:
                return 0
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM missions WHERE status = %s", (status,))
                result = cursor.fetchone()
            
            conn.close()
            count = result[0]
            return count
        except Error as e:
            print(f"Error: {e}")
            return 0
    
    def count_open_missions(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return 0
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM missions WHERE status IN ('ASSIGNED', 'IN_PROGRESS')")
                result = cursor.fetchone()
            
            conn.close()
            count = result[0]
            return count
        except Error as e:
            print(f"Error: {e}")
            return 0
    
    def count_critical_missions(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return 0
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM missions WHERE risk_level = 'CRITICAL'")
                result = cursor.fetchone()
            
            conn.close()
            count = result[0]
            return count
        except Error as e:
            print(f"Error: {e}")
            return 0
    
    def get_top_agent(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM agents ORDER BY completed_missions DESC LIMIT 1")
                agent = cursor.fetchone()
            
            conn.close()
            return agent
        except Error as e:
            print(f"Error: {e}")
            return None