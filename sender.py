import time
import os
import socket
import os
import subprocess
import logging
import sys
import gpiozero
import threading

SERVER_ADDR = "192.168.1.100"
ROUTER_ADDR = "192.168.1.128"
SERVER_DB_PATH = "/home/david/car_scanner"
LOCAL_DB_PATH = "/home/david/car_scanner/obd_data.db"
SERVER_USER = "david"
LED_GREEN = 24

led_green = gpiozero.LED(LED_GREEN)


def is_wifi_connected():
    logging.debug("sending a packet to 192.168.1.128 on port 53")
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ROUTER_ADDR, 53))
        logging.info("raspb is connected to home wifi")
        return True
    except socket.error as ex:
        logging.warning(ex)
        return False
    
def blink_led():
    while blinking:
        led_green.on()
        time.sleep(0.5)
        led_green.off()
        time.sleep(0.5)

def send_data():
    global blinking

    blinking = True
    blink_thread = threading.Thread(target=blink_led)
    blink_thread.start()

    try:
        logging.info("Sending data to server...")
        os.system(f"scp {LOCAL_DB_PATH} {SERVER_USER}@{SERVER_ADDR}:{SERVER_DB_PATH}")
        logging.info("Data sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send data: {e}")
    finally:
        blinking = False
        blink_thread.join()


def monitor_and_send_data():
    logging.info("monitoring and sending data")
    while True:
        logging.debug("checking if the rasp is connected to wifi")
        if is_wifi_connected():
            logging.debug("connected!")
            led_green.on()
            send_data()
            led_green.on()
            time.sleep(60)
        else:
            led_green.off()
            logging.warning("Waiting to connect to home Wi-Fi...")
        time.sleep(15)  # Check every 15 seconds

if __name__ == "__main__":
    sys.stderr = open("stderr_sender.log", "a")
    sys.stdout = open("stdout_sender.log", "a")
    logging.basicConfig(filename='sender.log', format='%(asctime)s: %(message)s',
                    level=logging.DEBUG)
    monitor_and_send_data()
    