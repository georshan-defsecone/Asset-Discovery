# scan_runner.py
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.get_inputs import get_input_data
from utils.wmiconnect import connect_and_execute as connect_wmi
# from winrm import connect_and_execute as connect_winrm
from utils.logging_config import setup_logging
from utils.store_data import create_db_and_store_results

logger = setup_logging()

def is_port_open(ip, port, timeout=1):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def run_scan(project_name, username, password, domain, ip_input, serverip):
    logger.info("Starting asset discovery")

    input_data = get_input_data(ip_input)
    if "error" in input_data:
        logger.error(f"Input error: {input_data['error']}")
        return {"status": "error", "message": input_data["error"]}

    ips = input_data['ips']
    max_threads = 10

    def scan(ip):
        logger.info(f"Checking services on {ip}...")

        # winrm_http_open = is_port_open(ip, 5985)
        # winrm_https_open = is_port_open(ip, 5986)
        wmi_open = is_port_open(ip, 135)
        try:
            # Prefer WinRM if available
            if wmi_open:
                logger.info(f"WMI port 135 open on {ip}. Attempting WMI connection.")
                if connect_wmi(project_name, ip, username, password, domain, serverip):
                    logger.info(f"WMI scan successful for {ip}")
                else:
                    logger.warning(f"WMI scan failed for {ip}")
            else:
                logger.warning(f"No known management ports open on {ip}. Skipping.")
                # project_name = project_name
                ip = ip
                system_name = ''
                status = "Failed"
                data = "Port Closed"
                create_db_and_store_results(project_name, ip, system_name, status, data)

        except Exception as e:
            logger.error(f"Error during scan for {ip}: {str(e)}")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(scan, ip) for ip in ips]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Thread execution error: {str(e)}")

    return {"status": "success", "message": "Scan complete"}


##########################

#    Evil Winrm

##########################

    #     try:
    #         # Prefer WinRM if available
    #         if winrm_http_open or winrm_https_open:
    #             logger.info(f"WinRM port {'5985' if winrm_http_open else '5986'} open on {ip}. Attempting WinRM connection.")
    #             if connect_winrm(project_name, ip, username, password, domain, serverip):
    #                 logger.info(f"WinRM scan successful for {ip}")
    #                 return
    #             else:
    #                 logger.warning(f"WinRM scan failed for {ip}")
    #                 # Try WMI if also open
    #                 if wmi_open:
    #                     logger.info(f"Falling back to WMI on {ip}")
    #                     if connect_wmi(project_name, ip, username, password, domain, serverip):
    #                         logger.info(f"WMI scan successful for {ip}")
    #                     else:
    #                         logger.warning(f"WMI scan also failed for {ip}")
    #                 else:
    #                     logger.warning(f"No fallback option available for {ip}")
    #         elif wmi_open:
    #             logger.info(f"WMI port 135 open on {ip}. Attempting WMI connection.")
    #             if connect_wmi(project_name, ip, username, password, domain, serverip):
    #                 logger.info(f"WMI scan successful for {ip}")
    #             else:
    #                 logger.warning(f"WMI scan failed for {ip}")
    #         else:
    #             logger.warning(f"No known management ports open on {ip}. Skipping.")

    #     except Exception as e:
    #         logger.error(f"Error during scan for {ip}: {str(e)}")

    # with ThreadPoolExecutor(max_workers=max_threads) as executor:
    #     futures = [executor.submit(scan, ip) for ip in ips]
    #     for future in as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             logger.error(f"Thread execution error: {str(e)}")

    # return {"status": "success", "message": "Scan complete"}
