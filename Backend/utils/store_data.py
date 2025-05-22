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



def extract_json_to_csv(db_path, csv_output_path):
    """
    Extracts fields from an SQLite database table and writes them to a CSV file.
    Handles both 'pass' (with JSON) and 'fail' (with status message) rows.
    """

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all rows from the scan_results table
    cursor.execute("SELECT id, client_ip, system_name, status, json_data FROM scan_results")
    rows = cursor.fetchall()

    # CSV Headers
    headers = [
        "ID", "Client IP", "System Name", "Status", "Hostname", "OS Name",
        "License Status", "Disk Space (GB)", "RAM (GB)", "AV Status", "Firewall Status", "Raw JSON/Error"
    ]
    output_data = []

    for row in rows:
        id_, client_ip, system_name, status, json_data = row

        # Default fields for CSV row
        hostname = os_name = license_status = disk_space = ram = av_status = firewall_status = ""

        if status.lower() == "success":
            try:
                data = json.loads(json_data)

                asset = data.get("AssetDetails", {})
                hostname = asset.get("SystemName", "")
                disk_space = asset.get("DiskSpaceGB", "")
                ram = asset.get("Ram Size", "")

                # Extract from Hardware list
                for hw in data.get("Hardware", []):
                    if "OperatingSystem" in hw:
                        os_name = hw["OperatingSystem"].get("Operating System", "")
                    if "License" in hw:
                        license_status = hw["License"].get("LicenseStatus", "")

                # Extract from Security list
                for sec in data.get("Security", []):
                    if "Antivirus" in sec:
                        av_status = sec["Antivirus"].get("SignatureStatus", "")
                    if "Firewall" in sec:
                        profiles = sec["Firewall"]
                        if isinstance(profiles, list):
                            firewall_status = ", ".join([f"{p['Profile']}={p['Enabled']}" for p in profiles])
                        elif isinstance(profiles, dict):
                            firewall_status = profiles.get("Enabled", "")

                raw_json_or_error = ""  # clean JSON means no error here

            except (json.JSONDecodeError, TypeError) as e:
                raw_json_or_error = f"JSON Decode Error: {str(e)}"

        else:
            # If failed, JSON data will be a string like 'portclosed', etc.
            raw_json_or_error = json_data

        output_data.append([
            id_, client_ip, system_name, status,
            hostname, os_name, license_status,
            disk_space, ram, av_status, firewall_status, raw_json_or_error
        ])

    # Write to CSV
    with open(csv_output_path, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(output_data)

    #print(f"✅ Data exported to {csv_output_path}")

# if __name__ == "__main__":
#     db_path = "db/Test2.db"         
#     csv_path = "reports/final_report.csv"
#     extract_json_to_csv(db_path, csv_path)