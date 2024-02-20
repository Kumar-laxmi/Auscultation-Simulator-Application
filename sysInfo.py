import time
import psutil
from rpi_lcd import LCD

# Create an LCD object
lcd = LCD()

# Function to get CPU usage percentage
def get_cpu_usage():
    return f"CPU: {psutil.cpu_percent()}%"

# Function to get RAM usage information
def get_ram_info():
    ram = psutil.virtual_memory()
    return f"RAM: {ram.percent}% Used"

# Function to get Disk usage information
def get_disk_info():
    disk = psutil.disk_usage('/')
    return f"Disk: {disk.percent}% Used"

# Function to get IP Address
def get_ip_address():
    try:
        ip_address = psutil.net_if_addrs()['wlan0'][0].address  # Change 'wlan0' to your network interface
        return f"{ip_address}"
    except KeyError:
        return "IP: Not available"

# Function to update and scroll system information
def update_system_info(delay=1):
    try:
        while True:
            cpu_info = get_cpu_usage()
            ram_info = get_ram_info()
            disk_info = get_disk_info()

            lcd.text(cpu_info.ljust(16), 1)
            time.sleep(delay)
            lcd.text(ram_info.ljust(16), 1)
            time.sleep(delay)
            lcd.text(disk_info.ljust(16), 1)
            time.sleep(delay)
    except KeyboardInterrupt:
        lcd.clear()

# Function to display IP Address on the second line
def display_ip_address():
    try:
        while True:
            ip_address = get_ip_address()
            lcd.text(ip_address.ljust(16), 2)
            time.sleep(2)
    except KeyboardInterrupt:
        lcd.clear()

# Run the functions in parallel (multithreading)
import threading

update_thread = threading.Thread(target=update_system_info)
ip_thread = threading.Thread(target=display_ip_address)

try:
    update_thread.start()
    ip_thread.start()
    update_thread.join()
    ip_thread.join()
except KeyboardInterrupt:
    lcd.clear()
