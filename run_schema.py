import pymysql
import os

def run_schema():
    conn = pymysql.connect(host='localhost', user='root', database='tms')
    try:
        with conn.cursor() as cursor:
            with open('schema.sql', 'r') as f:
                sql_script = f.read()
                
            # Split by semicolon but ignore semicolons inside statements if there were any, though basic split is fine here.
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            for statement in statements:
                if statement:
                    cursor.execute(statement)
        conn.commit()
        print("Schema applied successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_schema()
