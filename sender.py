import time
import os
import socket
import os
import subprocess

def is_wifi_connected():
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("192.168.1.128", 53))
        return True
    except socket.error as ex:
        print(ex)
        return False

def send_data():
    try:
        print("Sending data to server...")
        os.system("scp obd_data.db david@192.168.1.100:/home/david/car_scanner")
        print("Data sent successfully.")
    except Exception as e:
        print(f"Failed to send data: {e}")

def monitor_and_send_data():
    while True:
        if is_wifi_connected():
            send_data()
            break  # Exit loop after successful data transfer
        else:
            print("Waiting to connect to home Wi-Fi...")
        time.sleep(15)  # Check every 15 seconds

if __name__ == "__main__":
    monitor_and_send_data()
