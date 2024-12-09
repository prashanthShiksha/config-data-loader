import os
import json
import psycopg2

# Database connection parameters
DB_CONFIG = {
    "dbname": "test2",
    "user": "root",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}

def create_table():
    try :
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            query = """
                CREATE TABLE IF NOT EXISTS local_report_config2 (
                id SERIAL PRIMARY KEY,
                report_name TEXT NOT NULL,
                question_type TEXT NOT NULL,
                config Json NOT NULL
            );
            """
            cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()

def insert_into_table(conn, report_name, question_type, query):
    """
    Insert a record into the report_config table.
    """
    try:
        with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO local_report_config2 (report_name, question_type, config)
                VALUES (%s, %s, %s);
            """
            cursor.execute(insert_query, (report_name, question_type, json.dumps(query)))
        conn.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()

def process_folders(main_folder_path):
    """
    Process the folder structure and insert data into the table.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        id_counter = 1  
        
        for folder_name in os.listdir(main_folder_path):
            folder_path = os.path.join(main_folder_path, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            report_name = folder_name  
            
            json_folder_path = os.path.join(folder_path, "json")
            if not os.path.exists(json_folder_path):
                print(f"No 'json' folder found in {folder_name}")
                continue
            
            for query_type in os.listdir(json_folder_path):
                query_type_path = os.path.join(json_folder_path, query_type)
                
                if not os.path.isdir(query_type_path):
                    continue
                
                for json_file in os.listdir(query_type_path):
                    json_file_path = os.path.join(query_type_path, json_file)
                    
                    if not json_file.endswith(".json"):
                        continue
                    
                    with open(json_file_path, "r") as f:
                        try:
                            query_data = json.load(f)
                        except json.JSONDecodeError as e:
                            print(f"Invalid JSON in file {json_file_path}: {e}")
                            continue
                    
                    # Insert into the database
                    insert_into_table(conn, report_name, query_type, query_data)
        
        print("All data processed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# Main folder path
main_folder = "/home/user1/Documents/meta-dash-python/projectJson"
create_table()
process_folders(main_folder)
