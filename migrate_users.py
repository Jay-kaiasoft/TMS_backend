from database import get_db

try:
    db = next(get_db())
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        cursor.execute("ALTER TABLE users ADD COLUMN city VARCHAR(100), ADD COLUMN state VARCHAR(100), ADD COLUMN country VARCHAR(100), ADD COLUMN zip VARCHAR(20), ADD COLUMN phone VARCHAR(20), ADD COLUMN is_sms_active BOOLEAN DEFAULT FALSE;")
        db.commit()
        print("Successfully added new columns to the 'users' table.")
except Exception as e:
    print(f"Error altering table: {e}")
