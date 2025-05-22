# store_data.py

import sqlite3
import logging
import os, json, logging, csv
import threading

db_lock = threading.Lock()


def create_db_and_store_results(project_name, client_ip, system_name, status, data):
    """
    Creates a new SQLite database for the scan and stores client IP and JSON data.
    """
    # import os, json, sqlite3, logging
    with db_lock:
        try:
            db_name = f"db/{project_name}.db"
            os.makedirs('db', exist_ok=True)

            # Connect to the database (it will be created if it doesn't exist)
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_ip TEXT NOT NULL,
                system_name TEXT NOT NULL,
                status TEXT NOT NULL,
                json_data TEXT NOT NULL
            )
            ''')

            # Insert the data (use correct column name: system_name)
            cursor.execute('''
            INSERT INTO scan_results (client_ip, system_name, status, json_data)
            VALUES (?, ?, ?, ?)
            ''', (client_ip, system_name, status, json.dumps(data)))

            # Commit and close
            conn.commit()
        except sqlite3.OperationalError as e:
            logging.error(f"[!] SQLite error on {client_ip}: {e}")
        finally:
            conn.close()
    # conn.close()
    # logging.info(f"Scan data stored in {db_name} for client IP: {client_ip}")



# import sqlite3
# import json
# import csv

def extract_json_to_csv(db_path: str, csv_output_path: str):
    """
    Extracts selected fields from JSON data in an SQLite table and writes them to a CSV file.

    Parameters:
        db_path (str): Path to the SQLite database.
        csv_output_path (str): Path to save the CSV file.
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute query to fetch all json_data rows
    cursor.execute("SELECT json_data FROM scan_results")
    rows = cursor.fetchall()

    # Define the desired headers and initialize output
    headers = ["IP", "Hostname", "OS Name", "License Status", "Disk Space", "Ram", "AV Status", "Firewall Status"]
    output_data = []

    for row in rows:
        try:
            data = json.loads(row[0])  # Load JSON

            ip = data.get("System", {}).get("IPAddress", "")
            hostname = data.get("System", {}).get("Hostname", "")
            os_activated = data.get("OS", {}).get("Activated", "")
            av_status = data.get("Security", [{}])[0].get("Antivirus", {}).get("SignatureStatus", "")
            firewall_status = data.get("Security", [{}])[0].get("Firewall", {}).get("Status", "")

            output_data.append([
                ip, hostname, os_activated, av_status, firewall_status
            ])
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON row: {e}")

    conn.close()

    # Write to CSV
    with open(csv_output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(output_data)

    print(f"✅ Data written to {csv_output_path}")
