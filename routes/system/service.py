from fastapi import HTTPException

class SystemService:
    @staticmethod
    def get_navigation_menu(user_email: str, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id, role_id FROM users WHERE email=%s", (user_email,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            role_id = user['role_id']
            
            sql = """
            SELECT f.id, f.name 
            FROM functionalities f
            """
            cursor.execute(sql)
            all_functionalities = cursor.fetchall()
    
            # Fetch all modules to map them to functionalities
            cursor.execute("SELECT id, functionality_id, name FROM modules")
            all_modules = cursor.fetchall()
            
            menu_items = []
            projects_items = []
            settings_items = []
    
            for func in all_functionalities:
                title = func['name'].title()
                path = f"/{func['name'].replace(' ', '-')}"
    
                func_modules = [m['name'] for m in all_modules if m['functionality_id'] == func['id']]
                module_name = func_modules[0] if func_modules else ""
                
                item = {
                    "id": func['id'], 
                    "title": title, 
                    "path": path,
                    "permission": {
                        "functionality_name": func['name'],
                        "module_name": module_name,
                        "actions": [4]
                    }
                }
                
                if title in ["Manage Project", "Manage Tickets"]:
                    projects_items.append(item)
                else:
                    settings_items.append(item)
            
            # Always add the root dashboard
            menu_items.append({
                "partition": None,
                "items": [
                    {"id": "dashboard-root", "title": "Dashboard", "path": ""}
                ]
            })
    
            if projects_items:
                menu_items.append({
                    "partition": "Projects",
                    "items": projects_items
                })
                
            if settings_items:
                menu_items.append({
                    "partition": "Settings",
                    "items": settings_items
                })
            
            return menu_items
