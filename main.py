import logging
import sqlite3
import threading
import time
import subprocess 
import sys
import json 

from Car import Car
from OBD import OBD
from DB import DB
from Led import Led

import gpiozero




stop_event = threading.Event()


def monitoring(car: Car, obd_conn: OBD, db: DB, scanning_interval: float, sensors: list):
    while not stop_event.is_set():
        # check if the car is on and the obd is connected, start monitoring the sensors every 10 seconds
        if car.is_car_on() and obd_conn.is_connected():
            sensors_data = car.read_sensors(sensors)
            db.insert_data_sensors(sensors_data)
            time.sleep(scanning_interval)
        else:
            if obd_conn.is_connected():
                obd_conn.disconnect_obd()
                obd_conn.disconnect_bluetooth()
            while not obd_conn.is_connected() and not car.is_car_on():
                if not stop_event.is_set():
                    obd_conn.connect_bluetooth()
                    time.sleep(300)
                else:
                    break

        time.sleep(2)

def connected_to_wifi(addr: str):
    try:
        output = subprocess.run(["ping", "-c", "1", addr], capture_output=True)
        if output.returncode == 0:
            return True
        return False
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return False

def send_wifi_db(router_addr: str, db: DB, server_addr: str, server_db_path: str, server_user: str):
    while not stop_event.is_set():
        if connected_to_wifi(router_addr):
            db.send_db(server_addr, server_db_path, server_user)


def shutdown(switch_pin: int):
    # check switch status
    switch = gpiozero.Button(switch_pin)
    switch.wait_for_press()
    stop_event.set()

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def main():
    # setup logging
    sys.stderr = open("stderr.log", "a")
    sys.stdout = open("stdout.log", "a")
    logging.basicConfig(filename='reader.log', format='%(asctime)s: %(message)s',
                    level=logging.DEBUG)
    
    # Load the configuration
    config = load_config('config.json')

    # Access configuration values
    SCANNING_INTERVAL = config["SCANNING_INTERVAL"]
    SENSORS = config["SENSORS"]
    MAC_ADDR = config["MAC_ADDR"]
    SERVER_ADDR = config["SERVER_ADDR"]
    ROUTER_ADDR = config["ROUTER_ADDR"]
    SERVER_DB_PATH = config["SERVER_DB_PATH"]
    LOCAL_DB_PATH = config["LOCAL_DB_PATH"]
    SERVER_USER = config["SERVER_USER"]
    LED_GREEN = config["LED_GREEN"]
    LED_RED = config["LED_RED"]
    LED_BLUE = config["LED_BLUE"]
    SWITCH = config["SWITCH"]


    led_red = Led(LED_RED)
    led_green = Led(LED_GREEN)
    led_blue = Led(LED_BLUE)

    db = DB(LOCAL_DB_PATH, SENSORS)
    obd_conn = OBD(MAC_ADDR)
    car = Car(obd_conn)


    # 3 threads 
    # - monitoring the sensors
    # - sending the data to the server
    # - switch to shutdown the program

    global stop_event
    stop_event = threading.Event()

    monitoring_thread = threading.Thread(target=monitoring, args=(car, obd_conn, db, SCANNING_INTERVAL, SENSORS))
    sending_thread = threading.Thread(target=send_wifi_db, args=(ROUTER_ADDR, SERVER_ADDR, SERVER_DB_PATH, SERVER_USER))
    shutdown_thread = threading.Thread(target=shutdown, args=(SWITCH))

    monitoring_thread.start()
    sending_thread.start()
    shutdown_thread.start()


    monitoring_thread.join()
    sending_thread.join()
    shutdown_thread.join()


if __name__ == "__main__":
    main()