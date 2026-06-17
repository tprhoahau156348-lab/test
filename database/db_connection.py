import mysql.connector
from mysql.connector import Error

class DB_Connection:
    
    def __init__(self, host="localhost", user="root", password="1234", database="Intelligence_db"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def get_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def create_database(self):
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"[OK] Database '{self.database}' created or already exists")
            return True
        except Error as e:
            print(f"[FAIL] Error creating database: {e}")
            return False
    
    def create_tables(self):
        try:
            conn = self.get_connection()
            if not conn:
                print("[FAIL] Could not connect to database for table creation")
                return False
            
            with conn.cursor() as cursor:
                agents_table = """
                CREATE TABLE IF NOT EXISTS agents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    specialty VARCHAR(50) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    completed_missions INT DEFAULT 0,
                    failed_missions INT DEFAULT 0,
                    agent_rank ENUM('Junior', 'Senior', 'Commander') NOT NULL
                )
                """
                cursor.execute(agents_table)
                print("[OK] Agents table created or already exists")
                
                missions_table = """
                CREATE TABLE IF NOT EXISTS missions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    location VARCHAR(50) NOT NULL,
                    difficulty INT NOT NULL,
                    importance INT NOT NULL,
                    status VARCHAR(50) DEFAULT 'NEW',
                    risk_level VARCHAR(50),
                    assigned_agent_id INT,
                    FOREIGN KEY (assigned_agent_id) REFERENCES agents(id)
                )
                """
                cursor.execute(missions_table)
                print("[OK] Missions table created or already exists")
            
            conn.close()
            return True
        except Error as e:
            print(f"[FAIL] Error creating tables: {e}")
            return False
       

# בבנאי אני מגדיר את כל פרטי ההתחברות והיצירה של הקונטיינר שלא יעשו לי שטויות מי שישתמש בזה 
# במתודה get_connection , אני משתמש בפרטים שהזנתי בבנאי בשביל להתחבר לקונטיינר וכמובן בשביל למנוע תקלות למיניהם אני שם try לתפוס שלל שגיאות
# במתודה create_database אני מייצר את ה-database 
# במתודה  create_tables אני מייצר את שתי הטבלאות שלנו וגם להם אני עושה try על כל שגיאה שלא תבוא ח"ו
#  אני זורע הרבה print כתחליף ללוגים שלא ביקשו שנעשה, שיהיה קל לעקוב ולראות שהכל רץ כתיקונו