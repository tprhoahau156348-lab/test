import mysql.connector
from mysql.connector import Error
from .db_connection import DB_Connection

class AgentDB:
    
    VALID_RANKS = ['Junior', 'Senior', 'Commander']
    
    def __init__(self):
        self.db = DB_Connection()
    
    def create_agent(self, data):
        try:
            rank = data.get('agent_rank')
            if rank not in self.VALID_RANKS:
                return {"success": False, "message": f"Invalid rank. Must be one of: {', '.join(self.VALID_RANKS)}"}
            
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                query = "INSERT INTO agents (name, specialty, is_active, completed_missions, failed_missions, agent_rank) VALUES (%s, %s, %s, %s, %s, %s)"
                name = data.get('name')
                specialty = data.get('specialty')
                is_active = data.get('is_active', True)
                completed = data.get('completed_missions', 0)
                failed = data.get('failed_missions', 0)
                
                values = (name, specialty, is_active, completed, failed, rank)
                cursor.execute(query, values)
                conn.commit()
                agent_id = cursor.lastrowid
            
            conn.close()
            agent = self.get_agent_by_id(agent_id)
            return {"success": True, "data": agent}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def get_all_agents(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM agents")
                agents = cursor.fetchall()
            
            conn.close()
            if agents:
                return agents
            else:
                return []
        except Error as e:
            print(f"Error: {e}")
            return []
    
    def get_agent_by_id(self, agent_id):
        try:
            conn = self.db.get_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM agents WHERE id = %s", (agent_id,))
                agent = cursor.fetchone()
            
            conn.close()
            if agent:
                return agent
            else:
                return None
        except Error as e:
            print(f"Error: {e}")
            return None
    
    def update_agent(self, agent_id, data):
        try:
            agent = self.get_agent_by_id(agent_id)
            if not agent:
                return {"success": False, "message": "Agent not found"}
            
            name = data.get('name', agent['name'])
            specialty = data.get('specialty', agent['specialty'])
            is_active = data.get('is_active', agent['is_active'])
            agent_rank = data.get('agent_rank', agent['agent_rank'])
            
            if agent_rank not in self.VALID_RANKS:
                return {"success": False, "message": f"Invalid rank. Must be one of: {', '.join(self.VALID_RANKS)}"}
            
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                query = "UPDATE agents SET name = %s, specialty = %s, is_active = %s, agent_rank = %s WHERE id = %s"
                cursor.execute(query, (name, specialty, is_active, agent_rank, agent_id))
                conn.commit()
            
            conn.close()
            updated_agent = self.get_agent_by_id(agent_id)
            return {"success": True, "data": updated_agent}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def deactivate_agent(self, agent_id):
        try:
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                cursor.execute("UPDATE agents SET is_active = FALSE WHERE id = %s", (agent_id,))
                conn.commit()
            
            conn.close()
            return {"success": True, "message": "Agent deactivated successfully"}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def increment_completed(self, agent_id):
        try:
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                cursor.execute("UPDATE agents SET completed_missions = completed_missions + 1 WHERE id = %s", (agent_id,))
                conn.commit()
            
            conn.close()
            return {"success": True, "message": "Completed missions count incremented"}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def increment_failed(self, agent_id):
        try:
            conn = self.db.get_connection()
            if not conn:
                return {"success": False, "message": "Database connection failed"}
            
            with conn.cursor() as cursor:
                cursor.execute("UPDATE agents SET failed_missions = failed_missions + 1 WHERE id = %s", (agent_id,))
                conn.commit()
            
            conn.close()
            return {"success": True, "message": "Failed missions count incremented"}
        except Error as e:
            return {"success": False, "message": str(e)}
    
    def get_agent_performance(self, agent_id):
        try:
            agent = self.get_agent_by_id(agent_id)
            if not agent:
                return {"completed": 0, "failed": 0, "total": 0, "success_rate": 0}
            
            completed = agent['completed_missions']
            failed = agent['failed_missions']
            total = completed + failed
            
            success_rate = 0
            if total > 0:
                success_rate = completed / total
                success_rate = success_rate * 100
                success_rate = round(success_rate, 2)
            
            return {"completed": completed, "failed": failed, "total": total, "success_rate": success_rate}
        except Exception as e:
            print(f"Error: {e}")
            return {"completed": 0, "failed": 0, "total": 0, "success_rate": 0}
    
    def count_active_agents(self):
        try:
            conn = self.db.get_connection()
            if not conn:
                return 0
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM agents WHERE is_active = TRUE")
                result = cursor.fetchone()
            
            conn.close()
            count = result[0]
            return count
        except Error as e:
            print(f"Error: {e}")
            return 0