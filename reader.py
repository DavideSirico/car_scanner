import logging
import os
import obd
import time
import sqlite3
import subprocess
import sys
import gpiozero
import threading
import signal

DB_PATH = "/home/david/car_scanner/obd_data.db"
SCANNING_INTERVALL = 10 # in seconds 
SENSORS = ["ENGINE_LOAD", "COOLANT_TEMP", "FUEL_PRESSURE", "INTAKE_PRESSURE", "SPEED",
            "INTAKE_TEMP", "MAF", "THROTTLE_POS", "RUN_TIME", "FUEL_LEVEL",
            "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CATALYST_TEMP_B1S2",
            "CATALYST_TEMP_B2S2", "RELATIVE_THROTTLE_POS", "AMBIANT_AIR_TEMP",
            "RELATIVE_ACCEL_POS", "FUEL_RATE"]

MAC_ADDR = "13:E0:2F:8D:54:A9"
# IOS obd_mac_addr = "D2:E0:2F:8D:54:A9"

LED_RED = 16
LED_BLUE = 6
SWITCH = 3

running = True

led_red = gpiozero.PWMLED(LED_RED)
led_blue = gpiozero.PWMLED(LED_BLUE)
switch = gpiozero.Button(SWITCH)

def connect_sql():
    logging.info("connecting to SQL...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = " REAL, ".join(x for x in SENSORS) + " REAL)"
    query = "CREATE TABLE IF NOT EXISTS obd_data (timestamp DATE DEFAULT (datetime('now','localtime')), " + query
    logging.debug("creating table...")
    c.execute(query)
    return conn

def is_car_on(obd_connection):
    logging.info("checking if the car is responding...")
    response = obd_connection.query(obd.commands.RPM)
    if response and response.value is not None:
        logging.debug("Car is on and connected")
        return True
    return False

def gather_informations(obd_connection, sql_connection):
    logging.info("Monitoring car engine status...")

        
    sensor_data = []

    for sensor in SENSORS:
        logging.debug(f"reading {sensor}:")
        res = obd_connection.query(getattr(obd.commands, sensor), force=True)
        if res.value is not None: 
            logging.debug(res.value.magnitude)
            sensor_data.append(res.value.magnitude)
        else:
            sensor_data.append(None)

    logging.info("saving data")
    sql_connection.execute(
        "INSERT INTO obd_data (timestamp, " + ", ".join(SENSORS) + ") VALUES (datetime('now'), " + ", ".join(["?"] * len(SENSORS)) + ")", sensor_data
    )
    sql_connection.commit()
    logging.info("data saved")

def shutdown(signum, frame):
    global running
    logging.info("SHUTDOWN SIGN")
    running = False

def blink_blue_led():
    while blinking:
        led_blue.value = 0.2
        time.sleep(0.5)
        led_blue.off()
        time.sleep(0.5)


def connect_obd():
    global blinking
    # Start blinking the blue LED
    blinking = True
    blink_thread = threading.Thread(target=blink_blue_led)
    blink_thread.start()

    logging.info("Waiting for OBD-II connection...")

    # Try to connect to the OBD-II adapter
    try:
        logging.debug("connecting to obd scanner bluetooth...")

        os.system("/bin/bash -c \"bluetoothctl power on\"")
        os.system("/bin/bash -c \"bluetoothctl pairable on\"")
        os.system("/bin/bash -c \"bluetoothctl agent on\"")
        os.system("/bin/bash -c \"bluetoothctl default-agent\"")

        logging.debug("connecting...")
        os.system(f"/bin/bash -c \"bluetoothctl connect {MAC_ADDR}\"")
        
        logging.debug("pairing")
        os.system(f"/bin/bash -c \"bluetoothctl pair {MAC_ADDR}\"")
        
        logging.debug("trusting")
        os.system(f"/bin/bash -c \"bluetoothctl trust {MAC_ADDR}\"")


        obd.logger.setLevel(obd.logging.DEBUG)
        logging.info("connecting with the obd class")
        connection = obd.OBD("/dev/rfcomm0")  # Auto-connect to USB or Bluetooth OBD-II adapter

        return connection
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return None
    finally:
         # Stop blinking the blue LED
        blinking = False
        blink_thread.join()
    

def blink_red_led():
    while not running:
        led_red.value = 0.5
        time.sleep(0.5)
        led_red.off()
        time.sleep(0.5)

def shutdown_button():
    global running
    logging.info("SHUTDOWN SWITCH")
    blink_thread = threading.Thread(target=blink_red_led)
    blink_thread.start()
    running = False

if __name__ == "__main__":
    try:
        # setup logging
        sys.stderr = open("stderr_reader.log", "a")
        sys.stdout = open("stdout_reader.log", "a")
        logging.basicConfig(filename='reader.log', format='%(asctime)s: %(message)s',
                        level=logging.DEBUG)
        
        # turn on red led
        led_red.value = 0.5
        sql_connection = connect_sql()
        logging.info("CONNECTION WITH DATABASE SUCCESSFUL")

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        switch.when_released = shutdown_button
        
        os.system(f"/bin/bash -c \"rfcomm bind hci0 {MAC_ADDR}\"")
        obd_connection = None

        while running:
            if not running:
                break

            logging.info("OBD_CONNECTION STATUS:")
            if obd_connection is not None:
                logging.info(str(obd_connection.status()))
            else:
                logging.info("None")
            # controllo se sono connesso all'obd
            while obd_connection == None or obd_connection.status() != obd.OBDStatus.CAR_CONNECTED:
                if not running:
                    break  # Exit the loop if shutdown signal is received
                obd_connection = connect_obd()
                if (not obd_connection) or obd_connection.status() != obd.OBDStatus.CAR_CONNECTED:
                    led_blue.off()
                    logging.warning("Failed to connect to OBD-II adapter, retrying in 60 seconds...")
                    time.sleep(60)
                    continue

                if obd_connection.is_connected():
                    led_blue.value = 0.2
                    if is_car_on():
                        gather_informations(obd_connection, sql_connection)
                    logging.info(f"waiting for {SCANNING_INTERVALL}")
                    time.sleep(SCANNING_INTERVALL)
                
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Cleaning up resources...")
        led_red.off()
        sql_connection.close()
        time.sleep(10)
        logging.info("Program terminated gracefully.")

        os.system("shutdown -h now")
