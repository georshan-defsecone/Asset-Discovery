from flask import Flask, render_template, request, send_file, jsonify
import os
import json
import logging
from datetime import datetime
from utils.scan_runner import run_scan
from utils.store_data import create_db_and_store_results
from flask_cors import CORS
import sqlite3
from flask import jsonify

app = Flask(__name__)
CORS(app)

# Create logs and reports directories if not exist
os.makedirs("logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "db")

# Setup logging to a file
log_file = "logs/server_requests.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

@app.before_request
def log_request_info():
    logging.info(f"Request from {request.remote_addr} {request.method} {request.path}")
    logging.info(f"Headers: {dict(request.headers)}")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def collect():
    try:
        data = request.get_json()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        system_name = data['AssetProjectDetails']['MachineName']
        client_ip = data['AssetProjectDetails']['ClientIp']
        project_name = data['AssetProjectDetails']['ProjectName']

        # File name and path
        base_name = f"{client_ip}_{system_name}_{timestamp}.json"
        json_path = os.path.join("reports", base_name)

        # Save JSON payload
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logging.info(f"Data received from {client_ip}, saved as {base_name}")

        status = "Success"
        create_db_and_store_results(project_name, client_ip, system_name, status, data)

        return {"status": "received"}, 200

    except Exception as e:
        logging.error(f"Error processing upload from {request.remote_addr}: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

@app.route('/download')
def download_script():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, '..', 'scripts', 'Agent.ps1')
    script_path = os.path.abspath(script_path)

    if os.path.exists(script_path):
        logging.info(f"Script downloaded by {request.remote_addr}")
        return send_file(
            script_path,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="Asset_discovery.ps1"
        )
    else:
        logging.warning(f"Download attempted by {request.remote_addr} but script not found at {script_path}.")
        return "Script not found", 404

@app.route('/start_scan', methods=['POST'])
def start_scan():
    try:
        project_name = request.form.get("project_name")
        username = request.form.get("username")
        password = request.form.get("password")
        domain = request.form.get("domain") or ""
        ip_input = request.form.get("ip_input")
        serverip = request.form.get("serverip")

        if not all([project_name, username, password, ip_input, serverip]):
            return jsonify({"message": "Missing required fields."}), 400

        result = run_scan(project_name, username, password, domain, ip_input, serverip)
        return jsonify({"message": result.get("message", "Scan started.")}), 200

    except Exception as e:
        logging.error(f"Scan start error: {str(e)}")
        return jsonify({"message": "Failed to start scan."}), 500
    
@app.route('/projects', methods=['GET'])
def list_projects():
    try:
        db_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db')
        db_files = [f for f in os.listdir(db_folder) if f.endswith('.db')]
        return {"projects": db_files}, 200
    except Exception as e:
        logging.error(f"Error listing projects: {str(e)}")
        return {"error": str(e)}, 500
    
@app.route('/project/<project_name>', methods=['GET'])
def get_project_devices(project_name):
    try:
        db_path = os.path.join(DB_DIR, f"{project_name}.db")
        print(f"Looking for DB in: {db_path}")
        
        if not os.path.exists(db_path):
            logging.error(f"Database not found at: {db_path}")
            return jsonify({"error": "Project database not found"}), 404

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Use correct table and column names
        cursor.execute("SELECT system_name, client_ip FROM scan_results")
        rows = cursor.fetchall()
        conn.close()

        devices = [{"name": row[0], "ip_address": row[1]} for row in rows]
        return jsonify({"devices": devices}), 200

    except Exception as e:
        logging.error(f"Error querying project DB '{project_name}': {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project_name>/asset/<asset_name>', methods=['GET'])
def get_asset_json(project_name, asset_name):
    db_path = os.path.join(DB_DIR, f"{project_name}.db")
    

    if not os.path.exists(db_path):
        return jsonify({'error': f'Database for project "{project_name}" not found'}), 404

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Make sure the table and column names match your schema
        cursor.execute("SELECT json_data FROM scan_results WHERE system_name = ?", (asset_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': f'Asset "{asset_name}" not found in project "{project_name}"'}), 404

        asset_json = json.loads(row[0])  # Convert the JSON string to a Python dict
        return jsonify(asset_json)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/project/<project_name>/asset/<asset_name>/pdf/', methods=['GET'])
def download_asset_pdf(project_name, asset_name):
    db_path = os.path.join(DB_DIR, f"{project_name}.db")
    print(f"[DEBUG] Project: {project_name}, Asset: {asset_name}")
    print(f"[DEBUG] DB Path: {db_path}")
    
    if not os.path.exists(db_path):
        print("[ERROR] Database file does not exist.")
        return jsonify({'error': f'Database for project \"{project_name}\" not found'}), 404

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # See which assets are present
        cursor.execute("SELECT system_name FROM scan_results")
        all_assets = cursor.fetchall()
        print("[DEBUG] Available assets in DB:", all_assets)
        
        cursor.execute("SELECT json_data FROM scan_results WHERE system_name = ?", (asset_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            print(f"[ERROR] Asset {asset_name} not found in database.")
            return jsonify({'error': f'Asset \"{asset_name}\" not found'}), 404

        print("[DEBUG] Asset found. Proceeding to generate PDF.")

        # (PDF generation logic stays the same)
        ...
        
    except Exception as e:
        print("[ERROR] Exception during PDF generation:", str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Run on port 80 as you mentioned
    app.run(host='0.0.0.0', port=80)
