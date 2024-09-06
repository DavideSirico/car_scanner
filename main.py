import logging
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

def monitoring(car: Car, obd_conn: OBD, db: DB, scanning_interval: float, sensors: list, server_addr: str, router_addr: str, server_db_path: str, server_user: str, led_blue: Led):
    while not stop_event.is_set():
        # check if the car is on and the obd is connected, start monitoring the sensors every 10 seconds
        if car.is_car_on() and obd_conn.is_connected():
            led_blue.on()
            sensors_data = car.read_sensors(sensors)
            db.insert_data_sensors(sensors_data)
            send_wifi_db(router_addr, db, server_addr, server_db_path, server_user)
            time.sleep(scanning_interval)
        else:
            # if the car is off but the obd is connected, disconnect the obd to let it sleep
            if obd_conn.is_connected():
                obd_conn.disconnect_obd()
                obd_conn.disconnect_bluetooth()
            # the the car is off and the obd is disconnected try every 5 minutes to reconnect
            while not obd_conn.is_connected() and not car.is_car_on():
                led_blue.off()
                if not stop_event.is_set():
                    obd_conn.connect_bluetooth()
                    time.sleep(300)
                else:
                    return
        
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


    led_red = Led(LED_RED, "red")
    led_green = Led(LED_GREEN, "green")
    led_blue = Led(LED_BLUE, "blue")

    db = DB(LOCAL_DB_PATH, SENSORS, led_green)
    obd_conn = OBD(MAC_ADDR, led_blue)
    car = Car(obd_conn)


    # 3 threads 
    # - monitoring the sensors
    # - sending the data to the server
    # - switch to shutdown the program

    global stop_event
    stop_event = threading.Event()

    monitoring_thread = threading.Thread(target=monitoring, args=(car, obd_conn, db, SCANNING_INTERVAL, SENSORS, SERVER_ADDR, ROUTER_ADDR, SERVER_DB_PATH, SERVER_USER, led_blue, led_green))
    shutdown_thread = threading.Thread(target=shutdown, args=(SWITCH))

    monitoring_thread.start()
    shutdown_thread.start()

    led_red.on()

    monitoring_thread.join()
    shutdown_thread.join()


    db.connection.close()
    obd_conn.disconnect_obd()
    obd_conn.disconnect_bluetooth()
    led_red.off()
    led_green.off()
    led_blue.off()

    logging.info("END OF PROGRAM")
    subprocess.run(["shutdown", "-h", "now"])


if __name__ == "__main__":
    main()

