from fastapi import HTTPException
import pymysql

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "tms"

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

class ProjectService:
    @staticmethod
    def create_project(project):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, first_name, last_name FROM users WHERE id = %s", (project.client_id,))
                client = cursor.fetchone()
                if not client:
                    raise HTTPException(status_code=400, detail="Invalid client_id. User does not exist.")
                
                cursor.execute("SELECT id FROM projects WHERE name = %s", (project.name,))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Project with this name already exists")
                
                cursor.execute("INSERT INTO projects (name, client_id) VALUES (%s, %s)", (project.name, project.client_id))
                conn.commit()
                new_id = cursor.lastrowid
                
                client_name = f"{client['first_name']} {client['last_name']}".strip()
                return {"id": new_id, "name": project.name, "client_id": project.client_id, "client_name": client_name}
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @staticmethod
    def get_all_projects():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:   # ensure dictionary cursor
                cursor.execute("""
                    SELECT
                        p.id,
                        p.name,
                        p.client_id,
                        u.first_name,
                        u.last_name,
                        COUNT(t.id) AS ticket_count,
                        GROUP_CONCAT(t.title SEPARATOR '|') AS ticket_titles
                    FROM projects p
                    LEFT JOIN users u ON p.client_id = u.id
                    LEFT JOIN tickets t ON t.project_id = p.id
                    GROUP BY p.id, p.name, p.client_id, u.first_name, u.last_name
                    ORDER BY p.id DESC
                """)
                results = cursor.fetchall()
                projects = []
                for row in results:
                    # Build client name
                    client_name = None
                    if row['first_name'] or row['last_name']:
                        client_name = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()

                    # Convert the pipe‑separated string into a Python list
                    ticket_titles = []
                    if row['ticket_titles']:
                        ticket_titles = row['ticket_titles'].split('|')

                    projects.append({
                        "id": row['id'],
                        "name": row['name'],
                        "client_id": row['client_id'],
                        "client_name": client_name,
                        "ticket_count": row['ticket_count'],
                        "ticket_titles": ticket_titles   # always a list
                    })
                return projects
        except Exception as e:
            # Log the full error for debugging
            print(f"Error in get_all_projects: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @staticmethod
    def get_project(project_id: int):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.name, p.client_id, u.first_name, u.last_name 
                    FROM projects p 
                    LEFT JOIN users u ON p.client_id = u.id 
                    WHERE p.id = %s
                """, (project_id,))
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Project not found")
                
                client_name = None
                if row['first_name'] or row['last_name']:
                    client_name = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
                    
                return {
                    "id": row['id'],
                    "name": row['name'],
                    "client_id": row['client_id'],
                    "client_name": client_name
                }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @staticmethod
    def update_project(project_id: int, project):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM projects WHERE id = %s", (project_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail="Project not found")
                    
                cursor.execute("SELECT id, first_name, last_name FROM users WHERE id = %s", (project.client_id,))
                client = cursor.fetchone()
                if not client:
                    raise HTTPException(status_code=400, detail="Invalid client_id. User does not exist.")
                
                cursor.execute("SELECT id FROM projects WHERE name = %s AND id != %s", (project.name, project_id))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Another project with this name already exists")
                
                cursor.execute("UPDATE projects SET name = %s, client_id = %s WHERE id = %s", (project.name, project.client_id, project_id))
                conn.commit()
                
                client_name = f"{client['first_name']} {client['last_name']}".strip()
                return {"id": project_id, "name": project.name, "client_id": project.client_id, "client_name": client_name}
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @staticmethod
    def delete_project(project_id: int):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM projects WHERE id = %s", (project_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail="Project not found")
                
                cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()
