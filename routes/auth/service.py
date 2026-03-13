import datetime
import random
import string
from fastapi import HTTPException
from schemas.user import UserRegister, SetPasswordReq, UserLogin, VerifyOTPReq
from core.security import verify_password, get_password_hash, create_access_token
from services.email_service import EmailService

class AuthService:
    
    @staticmethod
    def register_user(user: UserRegister, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            role_id = 1
            sql = "INSERT INTO users (first_name, last_name, email, role_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user.first_name, user.last_name, user.email, role_id))
            db.commit()
            
            subject = "Set Your TMS Password"
            context = {
                "subject": subject,
                "title": "Welcome to TMS!",
                "message": "We are excited to have you on board. Please set your password to activate your account.",
                "action_link": f"http://localhost:5173/set-password?token={user.email}",
                "action_text": "Set Password"
            }
            EmailService.send_email(user.email, subject, "email_template.html", context)
            
        return {"message": "Registration successful. Please check your email to set a password."}

    @staticmethod
    def set_password(req: SetPasswordReq, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id, is_active FROM users WHERE email=%s", (req.token,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="Invalid token/email")
                
            hashed_password = get_password_hash(req.new_password)
            sql = "UPDATE users SET password_hash=%s, is_active=True WHERE email=%s"
            cursor.execute(sql, (hashed_password, req.token))
            db.commit()
        return {"message": "Password set successfully. You can now login."}

    @staticmethod
    def login(req: UserLogin, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id, role_id, first_name, last_name, password_hash, is_active FROM users WHERE email=%s", (req.email,))
            user = cursor.fetchone()
            if not user or not user.get('password_hash'):
                raise HTTPException(status_code=400, detail="Invalid credentials")
                
            if not user['is_active']:
                raise HTTPException(status_code=400, detail="Account not active")
                
            if not verify_password(req.password, user['password_hash']):
                raise HTTPException(status_code=400, detail="Invalid credentials")
                
            # Build permissions object
            cursor.execute("SELECT name FROM roles WHERE id=%s", (user['role_id'],))
            role_record = cursor.fetchone()
            role_name = role_record['name'] if role_record else ""

            cursor.execute("SELECT modules_action_id FROM role_actions WHERE role_id=%s", (user['role_id'],))
            user_actions = [row['modules_action_id'] for row in cursor.fetchall()]

            cursor.execute("SELECT id, name FROM functionalities")
            funcs = cursor.fetchall()
            
            cursor.execute("SELECT id, functionality_id, name FROM modules")
            all_modules = cursor.fetchall()

            cursor.execute("SELECT module_id, action_id FROM modules_actions")
            mod_actions = cursor.fetchall()

            db.commit()

            functionalities_data = []
            for f in funcs:
                f_mods = []
                for m in [mod for mod in all_modules if mod['functionality_id'] == f['id']]:
                    m_actions = [ma['action_id'] for ma in mod_actions if ma['module_id'] == m['id']]
                    assigned_actions = list(set(m_actions) & set(user_actions))
                    f_mods.append({
                        "moduleName": m['name'],
                        "roleAssignedActions": assigned_actions
                    })
                functionalities_data.append({
                    "functionalityName": f['name'],
                    "modules": f_mods
                })
                
            user_data = {
                "rolename": role_name,
                "permissions": {"functionalities": functionalities_data},
                "firstName": user['first_name'],
                "lastName": user['last_name'],
            }

            token = create_access_token({"sub": req.email, "role_id": user['role_id'], "user_id": user['id']})
            
        return {
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user_details": user_data
            },
            "message": "Login successful"
        }

    @staticmethod
    def verify_otp(req: VerifyOTPReq, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id, role_id , first_name , last_name FROM users WHERE email=%s", (req.email,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            sql = "SELECT id FROM otps WHERE user_id=%s AND code=%s AND is_used=False AND expires_at > NOW()"
            cursor.execute(sql, (user['id'], req.otp))
            otp_record = cursor.fetchone()
            
            if not otp_record:
                raise HTTPException(status_code=400, detail="Invalid or expired OTP")
                
            cursor.execute("UPDATE otps SET is_used=True WHERE id=%s", (otp_record['id'],))
            
            # Build permissions object
            cursor.execute("SELECT name FROM roles WHERE id=%s", (user['role_id'],))
            role_record = cursor.fetchone()
            role_name = role_record['name'] if role_record else ""

            cursor.execute("SELECT action_id FROM role_actions WHERE role_id=%s", (user['role_id'],))
            user_actions = [row['action_id'] for row in cursor.fetchall()]

            cursor.execute("SELECT id, name FROM functionalities")
            funcs = cursor.fetchall()
            
            cursor.execute("SELECT id, functionality_id, name FROM modules")
            all_modules = cursor.fetchall()

            cursor.execute("SELECT module_id, action_id FROM modules_actions")
            mod_actions = cursor.fetchall()

            db.commit()

            functionalities_data = []
            for f in funcs:
                f_mods = []
                for m in [mod for mod in all_modules if mod['functionality_id'] == f['id']]:
                    m_actions = [ma['action_id'] for ma in mod_actions if ma['module_id'] == m['id']]
                    assigned_actions = list(set(m_actions) & set(user_actions))
                    f_mods.append({
                        "moduleName": m['name'],
                        "roleAssignedActions": assigned_actions
                    })
                functionalities_data.append({
                    "functionalityName": f['name'],
                    "modules": f_mods
                })
                
            user_data = {
                "rolename": role_name,
                "subUser": False,
                "permissions": {"functionalities": functionalities_data},
                "firstName": user['first_name'],
                "lastName": user['last_name'],
            }

            token = create_access_token({"sub": req.email, "role_id": user['role_id'], "user_id": user['id']})
            
        return {
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user_details": user_data
            },
            "message": "Login successful"
        }

    @staticmethod
    def forgot_password(email: str, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                subject = "Reset Your TMS Password"
                context = {
                    "subject": subject,
                    "title": "Password Reset Request",
                    "message": "We received a request to reset your password. If you didn't make this request, you can safely ignore this email.",
                    "action_link": f"http://localhost:5173/set-password?token={email}",
                    "action_text": "Reset Password"
                }
                EmailService.send_email(email, subject, "email_template.html", context)
                
        return {"message": "If that email exists, a reset link has been sent."}
