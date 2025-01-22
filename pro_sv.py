import subprocess
import logging
from datetime import datetime
import sys

# Define color codes 
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m' # No color 

# Log file 
LOG_FILE = "./check_log.log"

# File with IP addresses 
CONFIG_FILE = "./ip_addres.conf"

# Logging configuration
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

# Check if configuration file exists
import os
if not os.path.isfile(CONFIG_FILE):
    message = f"Configuration file {CONFIG_FILE} not found."
    print(message)
    logging.info(message)
    exit(1)

# Function to check IP availability 
def check_ip(ip, name):
    try:
        subprocess.check_output(["ping", "-c", "3", ip], stderr=subprocess.STDOUT)
        message = f"{GREEN}{datetime.now()}: {name} on IP-{ip} OK - available{NC}"
        print(message)
        logging.info(message)
        return True
    except subprocess.CalledProcessError:
        message = f"{RED}{datetime.now()}: {name} on IP-{ip} is unreachable{NC}"
        print(message)
        logging.info(message)
        return False

# Function to check port availability with timeout 
def check_port(ip_port):
    ip, port = ip_port.split(':')
    try:
        # Check the port using /dev/tcp with a 5-second timeout 
        subprocess.check_output(["timeout", "5", "bash", "-c", f"echo > /dev/tcp/{ip}/{port}"], stderr=subprocess.DEVNULL)
        message = f"{GREEN}{datetime.now()}: Port {port} on {ip} is available{NC}"
        print(message)
        logging.info(message)
    except subprocess.CalledProcessError:
        message = f"{RED}{datetime.now()}: Port {port} on {ip} is unavailable or timeout{NC}"
        print(message)
        logging.info(message)

# Load associative array from configuration file 
IP_ADDRESSES = {}

with open(CONFIG_FILE, 'r') as config_file:
    for line in config_file:
        if '=' in line:  # Skip lines without equals sign
            key, value = line.strip().split('=', 1)
            IP_ADDRESSES[key] = value

# Function to handle interruption
def handle_interrupt():
    print("\nScript execution interrupted...")
    logging.info("Script execution interrupted.")
    sys.exit(0)

# Check IP and ports for each IP 
try:
    for name, ip_port in IP_ADDRESSES.items():
        print(f"Checking {name} ({ip_port})")

        # Check IP availability 
        ip, port = ip_port.split(':', 1)  # Split IP and port for checking 
        check_ip(ip, name)

        # If port is 'ANY', skip port check 
        if port == 'ANY':
            message = f"Port for {ip} set as 'ANY'. Skipping port check."
            print(message)
            logging.info(message)
        else:
            # Check port availability 
            check_port(ip_port)
except KeyboardInterrupt:
    handle_interrupt()