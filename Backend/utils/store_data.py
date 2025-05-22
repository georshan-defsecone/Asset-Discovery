# store_data.py

import sqlite3
import logging
import os, json, logging, csv, json
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

def extract_json_to_csv(db_path, csv_output_path):
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

    # Define the desired headers
    headers = ["IP", "Hostname", "OS Name", "License Status", "Disk Space (GB)", "RAM (GB)", "AV Status", "Firewall Status"]
    output_data = []

    for row in rows:
        try:
            data = json.loads(row[0])  # Load JSON string into a Python dict

            asset = data.get("AssetDetails", {})
            ip = asset.get("IPAddress", "")
            hostname = asset.get("SystemName", "")
            disk_space = asset.get("DiskSpaceGB", "")
            ram = asset.get("Ram Size", "")

            os_name = ""
            license_status = ""
            for hw in data.get("Hardware", []):
                if "OperatingSystem" in hw:
                    os_name = hw["OperatingSystem"].get("Operating System", "")
                if "License" in hw:
                    license_status = hw["License"].get("LicenseStatus", "")

            av_status = ""
            firewall_status = ""
            for sec in data.get("Security", []):
                if "Antivirus" in sec:
                    av_status = sec["Antivirus"].get("SignatureStatus", "")
                if "Firewall" in sec:
                    profiles = sec["Firewall"]
                    if isinstance(profiles, list):
                        firewall_status = ", ".join([f"{p['Profile']}={p['Enabled']}" for p in profiles])
                    elif isinstance(profiles, dict):
                        firewall_status = profiles.get("Enabled", "")

            output_data.append([
                ip, hostname, os_name, license_status, disk_space, ram, av_status, firewall_status
            ])

        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON row: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    conn.close()

    # Write to CSV
    with open(csv_output_path, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(output_data)

    print(f"✅ Data written to {csv_output_path}")

if __name__ == "__main__":
    db_path = "db/Test2.db"           # Update as needed
    csv_path = "reports/test.csv"     # Update as needed
    extract_json_to_csv(db_path, csv_path)
