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
from collections import OrderedDict
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import json
from fpdf import FPDF
import tempfile
import textwrap
from flask import Flask, send_file, jsonify
import sqlite3
import csv
import io
import os
from utils.store_data import extract_json_to_csv


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

        cursor.execute("SELECT json_data FROM scan_results WHERE system_name = ?", (asset_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': f'Asset "{asset_name}" not found in project "{project_name}"'}), 404

        # Use OrderedDict to preserve key order
        asset_json = json.loads(row[0], object_pairs_hook=OrderedDict)

        # Use Flask's Response with custom JSON encoder that respects OrderedDict order
        from flask import Response
        import json as pyjson

        return Response(
            pyjson.dumps(asset_json, indent=2),
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/project/<project_name>/asset/<asset_name>/pdf/', methods=['GET'])
def download_asset_pdf(project_name, asset_name):
    db_path = os.path.join(DB_DIR, f"{project_name}.db")
    if not os.path.exists(db_path):
        return jsonify({'error': f'Database for project "{project_name}" not found'}), 404

    try:
        # Retrieve JSON from DB
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT json_data FROM scan_results WHERE system_name = ?", (asset_name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': f'Asset "{asset_name}" not found in project "{project_name}"'}), 404

        json_data = json.loads(row[0])
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        y = height - 50
        left_margin = 40
        line_height = 15
        max_width = width - 2 * left_margin

        def check_page_space(y, lines_needed=1):
            if y < 60 + line_height * lines_needed:
                p.showPage()
                p.setFont("Helvetica", 10)
                return height - 50
            return y

        def draw_wrapped_text(key, value, y, indent=0):
            x = left_margin + indent
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x, y, f"{key}:")
            y -= line_height

            p.setFont("Helvetica", 10)
            text = str(value)
            words = text.split()
            line = ""
            for word in words:
                if p.stringWidth(line + word + " ", "Helvetica", 10) <= max_width - indent:
                    line += word + " "
                else:
                    p.drawString(x + 20, y, line.strip())
                    y = check_page_space(y)
                    y -= line_height
                    line = word + " "
            if line:
                y = check_page_space(y)
                p.drawString(x + 20, y, line.strip())
                y -= line_height
            return y

        def draw_dict(data, y, indent=0):
            for key, value in data.items():
                y = check_page_space(y)
                if isinstance(value, dict):
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(left_margin + indent, y, f"{key}:")
                    y -= line_height
                    y = draw_dict(value, y, indent + 20)
                elif isinstance(value, list):
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(left_margin + indent, y, f"{key}:")
                    y -= line_height
                    for idx, item in enumerate(value):
                        if isinstance(item, dict):
                            y = draw_dict(item, y, indent + 20)
                        else:
                            y = draw_wrapped_text(f"- Item {idx + 1}", item, y, indent + 20)
                else:
                    y = draw_wrapped_text(key, value, y, indent)
            return y

        def draw_section(title, section_data, y):
            y = check_page_space(y, 2)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, title)
            y -= line_height

            if isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict) and len(item) == 1:
                        for key, val in item.items():
                            y = check_page_space(y)
                            p.setFont("Helvetica-Bold", 10)
                            p.drawString(left_margin + 10, y, f"{key}:")
                            y -= line_height
                            if isinstance(val, dict):
                                y = draw_dict(val, y, indent=20)
                            elif isinstance(val, list):
                                for idx, subval in enumerate(val):
                                    if isinstance(subval, dict):
                                        y = check_page_space(y)
                                        p.setFont("Helvetica-Oblique", 10)
                                        p.drawString(left_margin + 20, y, f"- Item {idx + 1}")
                                        y -= line_height
                                        y = draw_dict(subval, y, indent=30)
                                    else:
                                        y = draw_wrapped_text(f"- Item {idx + 1}", subval, y, indent=30)
                            else:
                                y = draw_wrapped_text(key, val, y, indent=20)
                    elif isinstance(item, dict):
                        y = draw_dict(item, y, indent=10)
                    else:
                        y = draw_wrapped_text("Item", item, y, indent=10)
            elif isinstance(section_data, dict):
                y = draw_dict(section_data, y, indent=10)
            else:
                y = draw_wrapped_text(title, section_data, y, indent=10)

            y -= 10
            return y

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(left_margin, y, f"Asset Report: {asset_name}")
        y -= 30

        for section in ["AssetDetails", "Hardware", "Software", "Users", "Security"]:
            if section in json_data:
                y = draw_section(section, json_data[section], y)

        p.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"{asset_name}_details.pdf", mimetype='application/pdf')

    except Exception as e:
        return jsonify({'error': str(e)}), 500



    


@app.route("/projects/<project_name>/download", methods=["GET"])
def download_csv(project_name):
    try:
        db_path = f"db/{project_name}.db"
        if not os.path.exists(db_path):
            return jsonify({"error": "Project not found"}), 404

        # Create temp CSV file
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        temp_csv_path = temp_csv.name
        temp_csv.close()

        # Call your function to fill in the CSV
        extract_json_to_csv(db_path, temp_csv_path)

        # Send CSV to frontend
        return send_file(temp_csv_path,
                         as_attachment=True,
                         download_name=f"{project_name}_report.csv",
                         mimetype="text/csv")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    # Run on port 80 as you mentioned
    app.run(host='0.0.0.0', port=80)
