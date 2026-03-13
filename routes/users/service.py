from fastapi import HTTPException
from core.security import get_password_hash

class UserService:  
    @staticmethod
    def get_user_hierarchy(db):
        """
        Returns a hierarchical tree of users.
        Each node contains id, name, and data (list of child nodes with same structure).
        Only root users (report_to is null) appear at the top level.
        """
        with db.cursor() as cursor:
            # Assuming the correct column is 'role'
            cursor.execute("""
                SELECT * FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE r.name != 'Customer' AND u.is_active = true
                ORDER BY u.id
            """)
            all_users = cursor.fetchall()

            # Build mapping: manager_id -> list of direct reports (full user dicts)
            reports = {}
            for user in all_users:
                manager_id = user.get("report_to")
                if manager_id is not None:
                    reports.setdefault(manager_id, []).append(user)

            # Recursive function to build a node and its children
            def build_node(user):
                node = {
                    "id": user["id"],
                    "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    "data": []
                }
                for child in reports.get(user["id"], []):
                    node["data"].append(build_node(child))
                return node

            # Root users are those with no manager
            roots = [user for user in all_users if user.get("report_to") is None]

            # Build hierarchy starting from roots
            hierarchy = [build_node(root) for root in roots]

        return hierarchy
            
    @staticmethod
    def get_all_users(db):
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY id DESC")
            users = cursor.fetchall()
            return users

    @staticmethod
    def get_customers(db):
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE r.name = 'Customer' AND u.is_active = true
                ORDER BY u.id DESC
            """)
            customers = cursor.fetchall()
            return customers

    @staticmethod
    def get_non_customers(db):
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE r.name != 'Customer' AND u.is_active = true
                ORDER BY u.id DESC
            """)
            users = cursor.fetchall()
            return users

    @staticmethod
    def get_user(user_id: int, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

    @staticmethod
    def create_user(user, db):
        with db.cursor() as cursor:
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
                
            hashed_pw = get_password_hash(user.password)
            
            sql = """
                INSERT INTO users 
                (first_name, last_name, email, password_hash, role_id, city, state, country, zip, phone, is_sms_active, is_active, report_to, company_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            vals = (
                user.first_name, user.last_name, user.email, hashed_pw, user.role_id, 
                user.city, user.state, user.country, user.zip, user.phone, 
                user.is_sms_active, user.is_active, user.report_to, user.company_id
            )
            
            cursor.execute(sql, vals)
            db.commit()
            last_id = cursor.lastrowid
            
            # Fetch the newly created user
            cursor.execute("SELECT * FROM users WHERE id=%s", (last_id,))
            new_user = cursor.fetchone()
            
            return new_user

    @staticmethod
    def update_user(user_id: int, user_update, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="User not found")
                
            update_data = user_update.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="No valid fields to update")

            if "password" in update_data:
                update_data["password_hash"] = get_password_hash(update_data.pop("password"))

            set_clauses = [f"{key} = %s" for key in update_data.keys()]
            values = list(update_data.values())
            values.append(user_id)
            
            sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
            cursor.execute(sql, tuple(values))
            db.commit()
            
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            updated_user = cursor.fetchone()
            return updated_user

    @staticmethod
    def delete_user(user_id: int, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="User not found")
                
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            db.commit()
            return True