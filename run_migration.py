import pymysql

def run_migration():
    conn = pymysql.connect(host='localhost', user='root', database='tms')
    try:
        with conn.cursor() as cursor:
            # 1. Drop existing tables to recreate them with proper keys OR alter them
            # We'll just drop role_actions and modules_actions since they're just mappings, 
            # and re-insert the mappings.
            
            cursor.execute("DROP TABLE IF EXISTS role_actions;")
            cursor.execute("DROP TABLE IF EXISTS modules_actions;")
            
            # 2. Recreate modules_actions
            cursor.execute("""
            CREATE TABLE modules_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                module_id INT NOT NULL,
                action_id INT NOT NULL,
                UNIQUE KEY (module_id, action_id),
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
                FOREIGN KEY (action_id) REFERENCES actions(id) ON DELETE CASCADE
            );
            """)

            # 3. Recreate role_actions  
            cursor.execute("""
            CREATE TABLE role_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role_id INT NOT NULL,
                modules_action_id INT NOT NULL,
                UNIQUE KEY (role_id, modules_action_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (modules_action_id) REFERENCES modules_actions(id) ON DELETE CASCADE
            );
            """)

            # 4. Insert base module actions (1-Users, 2-Tickets)
            cursor.execute("""
            INSERT IGNORE INTO modules_actions (module_id, action_id) VALUES
            (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 1), (2, 2), (2, 3), (2, 4);
            """)
            
            # 5. Insert Status module actions (Module 4)
            cursor.execute("""
            INSERT IGNORE INTO modules_actions (module_id, action_id) VALUES
            (4, 1), (4, 2), (4, 3), (4, 4);
            """)

            # 6. Insert Projects module actions (Module 5)
            cursor.execute("""
            INSERT IGNORE INTO modules_actions (module_id, action_id) VALUES
            (5, 1), (5, 2), (5, 3), (5, 4);
            """)

            # 7. Insert Role Actions Mapping
            # (Matches exactly what we put in schema.sql)
            cursor.execute("""
            INSERT IGNORE INTO role_actions (role_id, modules_action_id) VALUES
            (1, 1), (1, 2), (1, 3), (1, 4), 
            (1, 5), (1, 6), (1, 7), (1, 8),
            (2, 8), (2, 6),                 
            (3, 8), (3, 5),
            (1, 9), (1, 10), (1, 11), (1, 12),
            (1, 13), (1, 14), (1, 15), (1, 16);
            """)
            
        conn.commit()
        print("Migration applied successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
