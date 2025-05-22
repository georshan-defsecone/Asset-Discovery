# winrm.py
import logging
import base64
from utils.logging_config import setup_logging
from utils.store_data import create_db_and_store_results
import winrm

# Set up the logger
logger = setup_logging()

def encode_powershell_command(command):
    return base64.b64encode(command.encode("utf-16le")).decode()

def connect_and_execute(project_name, ip, username, password, domain, server_ip):
    """Connects to the remote system via WinRM (HTTPS preferred, fallback to HTTP) and executes PowerShell script."""
    try:
        raw_ps = f"""
            $url = 'http://{server_ip}/download';
            $dest = 'C:\\Windows\\Temp\\script.ps1';
            Invoke-WebRequest -Uri $url -OutFile $dest;
            powershell -ExecutionPolicy Bypass -File $dest -ServerUrl 'http://{server_ip}/upload' -ProjectName {project_name}
        """
        encoded_cmd = encode_powershell_command(raw_ps)

        user = f"{domain}\\{username}" if domain else username

        # Try HTTPS first
        try:
            logger.info(f"Attempting WinRM HTTPS connection to {ip} on port 5986")
            session = winrm.Session(f'https://{ip}:5986/wsman',
                                    auth=(user, password),
                                    transport='ntlm',
                                    server_cert_validation='ignore')
            response = session.run_cmd("powershell.exe", ["-encodedcommand", encoded_cmd])
        except Exception as https_err:
            logger.warning(f"HTTPS connection to {ip} failed, trying HTTP: {https_err}")
            session = winrm.Session(f'http://{ip}:5985/wsman',
                                    auth=(user, password),
                                    transport='ntlm',
                                    server_cert_validation='ignore')
            response = session.run_cmd("powershell.exe", ["-encodedcommand", encoded_cmd])

        if response.status_code == 0:
            logger.info(f"[+] Output from {ip}:\n{response.std_out.decode()}")
            return True
        else:
            logger.error(f"[!] Error from {ip}:\n{response.std_err.decode()}")
            return False

    except Exception as e:
        logger.exception(f"[!] Exception on {ip}: {e}")
        return False
