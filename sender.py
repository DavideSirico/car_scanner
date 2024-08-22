import time
import os
import socket
import os
import subprocess
import logging

def is_wifi_connected():
    logging.debug("sending a packet to 192.168.1.128 on port 53")
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("192.168.1.128", 53))
        logging.info("raspb is connected to home wifi")
        return True
    except socket.error as ex:
        logging.warning(ex)
        return False

def send_data():
    try:
        logging.info("Sending data to server...")
        os.system("scp obd_data.db david@192.168.1.100:/home/david/car_scanner")
        logging.info("Data sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send data: {e}")

def monitor_and_send_data():
    logging.info("monitoring and sending data")
    while True:
        logging.debug("checking if the rasp is connected to wifi")
        if is_wifi_connected():
            logging.debug("connected!")
            send_data()
            break  # Exit loop after successful data transfer
        else:
            logging.warning("Waiting to connect to home Wi-Fi...")
        time.sleep(15)  # Check every 15 seconds

if __name__ == "__main__":
    logging.basicConfig(filename='01_sender.log', format='%(asctime)s: %(message)s',
                    level=logging.DEBUG)
    monitor_and_send_data()
