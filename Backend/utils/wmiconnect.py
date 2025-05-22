# wmiconnect.py
import subprocess
import logging
import os
import sys
import base64
from utils.logging_config import setup_logging
from utils.store_data import create_db_and_store_results

# Set up the logger from the centralized config
logger = setup_logging()

def encode_powershell_command(command):
    return base64.b64encode(command.encode("utf-16le")).decode()

def connect_and_execute(project_name, ip, username, password, domain, server_ip):
    r"""Downloads the PowerShell script to C:\Windows\Temp and executes it remotely."""
    try:
        raw_ps = rf"""
            $url = 'http://{server_ip}/download';
            $dest = 'C:\\Windows\\Temp\\script.ps1';
            Invoke-WebRequest -Uri $url -OutFile $dest;
            powershell -ExecutionPolicy Bypass -File $dest -ServerUrl 'http://{server_ip}/upload' -ProjectName {project_name} -scan_ip {ip};
            rm $dest
            """
        encoded = encode_powershell_command(raw_ps)

        user = f"{domain}/{username}" if domain else username
        wmiexec_path = os.path.abspath("venv/bin/wmiexec.py")

        cmd = [
            sys.executable,
            wmiexec_path,
            f"{user}:{password}@{ip}",
            f"powershell -EncodedCommand {encoded}"
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logger.info(f"[+] Output from {ip}:\n{result.stdout}")
            return True
        else:
            status = "Failed"
            data = "Error during login"
            system_name = ""
            create_db_and_store_results(project_name, ip, system_name, status, data)
            logger.error(f"[!] Error from {ip}:\n{result.stderr}")
            return False

    except Exception as e:
        logger.exception(f"[!] Exception on {ip}: {e}")
        return False

