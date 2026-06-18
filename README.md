# מערכת לניהול סוכנים ומשימות לשימוש יחידת מודעין. המערכת תכלול: שכבת הנתונים המלאה — חיבור ל-MySQL, יצירת טבלאות, ומחלקות OOP לניהול הנתונים. בנוסף חיבור של הכל לשרת HTTP.


## מבנה התקיות והקבצים
```
intelligence-task-manager/
├── main.py 
├──/database
│   ├── db_connection.py
│   ├── agent_db.py
│   └── mission_db.py
├──/routes
│  ├── agent_routes.py
│  ├── mission_routes.py
│  └── report_routes.py
├──/logs
│ └── app.log
├── README.md 
└── requirements.txt

```

## מבנה הטבלאות

### agents

שדה | סוג | הערות |
--- | --- | --- |
id | INT, AUTO_INCREMENT, PK |	מזהה ייחודי |
name |	VARCHAR |	שם הסוכן |
specialty |	VARCHAR |	תחום התמחות |
is_active |	BOOLEAN |	ברירת מחדל: TRUE |
completed_missions |	INT |	ברירת מחדל: 0 |
failed_missions |	INT |	ברירת מחדל: 0 |
agent_rank |	ENUM / VARCHAR |	Junior / Senior / Commander בלבד |


### missions

שדה |	סוג |	הערות |
--- | --- | --- |
id	| INT, AUTO_INCREMENT, PK |	מזהה ייחודי |
title |	VARCHAR |	כותרת המשימה |
description |	TEXT |	תיאור מפורט |
location |	VARCHAR |	מיקום |
difficulty |	INT |	1–10  בלבד |
importance |	INT	| 1–10 בלבד |
status |	VARCHAR |	ברירת מחדל: NEW |
risk_level |	VARCHAR |	מחושב אוטומטית — לא מגיע מהמשתמש |
assigned_agent_id |	INT	NULL | עד שיוך |


## הסבר על המחלקות והמודות

### מחלקה AgentDB
אחראית על כל פעולות SQL מול טבלת agents.
כלל: בכל מקום שלא נכתב במפורש מה להחזיר צריך להחזיר הודעת הצלחה או כישלון.

מתודה |	תפקיד |
--- | --- |
create_agent(data) |	יוצרת סוכן חדש ומחזירה את האובייקט של הסוכן
get_all_agents() |	מחזירה רשימת כל הסוכנים
get_agent_by_id(id)	| מחזירה סוכן אחד לפי ID, או None
update_agent(id, data) |	UPDATE לכל השורה (אין אפשרות לשנות id)
deactivate_agent(id) |	מגדירה מצב סוכן ללא פעיל
increment_completed(id) |	מעדכן את כמות המשימות שהושלמו 
increment_failed(id) |	מעדכן את כמות המשימות שנכשלו
get_agent_performance(id) |	מחזירה מילון עם המפתחות האלו completed, failed, total, success_rate
(שימו לב לחשב את הערך הזה success_rate - כמה באחוזים משימות הסתיימו בהצלחה מתוך הסך הכולל)
count_active_agents() |	מחזירה את מספר הסוכנים הפעילים 


### מחלקה MissionDB
אחראית על כל פעולות SQL מול טבלת missions.

מתודה |	תפקיד
--- | --- |
create_mission(data) | צירת משימה חדשה ומחזירה את כל האובייקט
get_all_missions() | זירה את כל המשימות
get_mission_by_id(id) |	מחזירה משימה אחת לפי ID, או None
assign_mission(m_id, a_id) |	משייכת משימה לסוכן
update_mission_status(id, status) |	משמשת לכל שינוי סטטוס
get_open_missions_by_agent(id) |	מחזירה משימות ASSIGNED/IN_PROGRESS של סוכן
count_all_missions() |	סה"כ משימות
count_by_status(status) |	סופרת לפי סטטוס מסוים
count_open_missions() |	סופרת משימות פתוחות
count_critical_missions() |	סופרת משימות CRITICAL
get_top_agent() |	הסוכן עם completed_missions הגבוה ביותר



### חוקי עסק שממומשים בשכבת הנתונים
```
1	rank חייב להיות Junior / Senior / Commander — כל ערך אחר זורק שגיאה.
2	difficulty ו-importance חייבים להיות בין 1 ל-10 — אחרת שגיאה.
3	risk_level מחושב אוטומטית בעת יצירת משימה — המשתמש לא שולח אותו.
4	סוכן עם is_active=False לא יכול לקבל משימות.
5	סוכן לא יכול להחזיק יותר מ-3 משימות פתוחות (ASSIGNED / IN_PROGRESS) במקביל.
6	אם risk_level=CRITICAL — רק סוכן בדרגת Commander יכול לקבל את המשימה.
7	ניתן לשייך רק משימה בסטטוס NEW. לאחר שיוך: status=ASSIGNED.
8	ניתן להתחיל רק משימה בסטטוס ASSIGNED. לאחר: status=IN_PROGRESS.
9	ניתן לסיים רק משימה. IN_PROGRESS  ולשנות לסטטוס failed or completed
10	ניתן לבטל רק משימה בסטטוס NEW או ASSIGNED — אחרת שגיאה.
```



## הקוד להרצת קונטיינר
``` bash
docker run -d --name intelligence-mysql -e MYSQL_ROOT_PASSWORD=1234 \
 -e MYSQL_DATABASE=Intelligence_db -p 3306:3306 mysql:8.0
```

## הקוד להרצת קובץ main
``` bash 
 python3 -m uvicorn main:app --reload
````

## agents דוגמא ליצירת שורה חדשה בטבלה
```bash 
{
  "name": "Yossi Cohen",
  "specialty": "Cyber",
  "is_active": true,
  "completed_missions": 0,
  "failed_missions": 0,
  "agent_rank": "Junior"
}
```
## דוגמא ליצירת שורה חדשה בטבלה missions

``` bash
{
  "title": "Routine Patrol",
  "description": "Standard border security sweep and camera inspection",
  "location": "North Sector",
  "difficulty": 3,
  "importance": 2
}
```