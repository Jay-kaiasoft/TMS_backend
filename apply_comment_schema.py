import pymysql
import os

def apply_comment_schema():
    conn = pymysql.connect(host='localhost', user='root', database='tms')
    try:
        with conn.cursor() as cursor:
            # 1. Add Manager role if not exists
            cursor.execute("INSERT IGNORE INTO roles (id, name) VALUES (4, 'Manager')")
            
            # 2. ticket_comments_type
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket_comments_type (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                created_by INT,
                created_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # 3. Insert types
            cursor.execute("INSERT IGNORE INTO ticket_comments_type (id, name) VALUES (1, 'Open'), (2, 'Private for Developer'), (3, 'Private for Customer'), (4, 'Private for manager'), (5, 'Admin only')")
            
            # 4. ticket_comments
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket_comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_id INT NOT NULL,
                comment LONGTEXT NOT NULL,
                parent_comment_id INT,
                comment_type_id INT,
                created_by INT,
                created_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_comment_id) REFERENCES ticket_comments(id) ON DELETE CASCADE,
                FOREIGN KEY (comment_type_id) REFERENCES ticket_comments_type(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # 5. ticket_comments_attachments
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket_comments_attachments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_comment_id INT NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_url VARCHAR(500) NOT NULL,
                created_by INT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_comment_id) REFERENCES ticket_comments(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
        conn.commit()
        print("Comment tables applied successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_comment_schema()
