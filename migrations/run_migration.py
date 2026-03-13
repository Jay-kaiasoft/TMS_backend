import pymysql

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "tms"

def run_migration():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    try:
        with conn.cursor() as cursor:
            # Check if column exists
            cursor.execute("SHOW COLUMNS FROM tickets LIKE 'status_id'")
            if not cursor.fetchone():
                print("Adding status_id column...")
                cursor.execute("ALTER TABLE tickets ADD COLUMN status_id INT DEFAULT NULL;")
                cursor.execute("ALTER TABLE tickets ADD CONSTRAINT fk_tickets_status FOREIGN KEY (status_id) REFERENCES status(id) ON DELETE SET NULL;")
                conn.commit()
                print("Migration successful.")
            else:
                print("status_id column already exists.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
