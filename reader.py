# sistema di soft-shutdown
# sistema di raccolta dati in formato prometheus?? o json/xml (servizio)
# script durante l'avvio
# collegamento all'obd
# sistema di logging
# gestione delle eccezioni
# controllare se sono a casa (collegato al wifi) e mandare i dati a 192.168.1.100


# 1. collegamento all'obd
import logging
import os
import obd
import time
import sqlite3
import subprocess
import sys

SENSORS = ["ENGINE_LOAD", "COOLANT_TEMP", "FUEL_PRESSURE", "INTAKE_PRESSURE", "SPEED",
            "INTAKE_TEMP", "MAF", "THROTTLE_POS", "RUN_TIME", "FUEL_LEVEL",
            "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CATALYST_TEMP_B1S2",
            "CATALYST_TEMP_B2S2", "RELATIVE_THROTTLE_POS", "AMBIANT_AIR_TEMP",
            "RELATIVE_ACCEL_POS", "FUEL_RATE"]

MAC_ADDR = "13:E0:2F:8D:54:A9"
# IOS obd_mac_addr = "D2:E0:2F:8D:54:A9"

def check_rfcomm_bind():
    logging.debug("Checking if there is already a RFCOMM connection with the OBD reader")
    try:
        # Running the rfcomm show command
        output = subprocess.check_output(["rfcomm"], text=True)
        
        # Checking if hci0 is mentioned in the output
        if MAC_ADDR in output:
            logging.info("RFCOMM bind to hci0 found.")
            return True
        else:
            logging.info("No RFCOMM bind to hci0 found.")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking RFCOMM: {e}")
        return False


def gather_informations(obd_connection, sql_connection):
    logging.info("Monitoring car engine status...")
    engine_running = True

    while engine_running:
        logging.info("checking if the car is still on")
        rpm = obd_connection.query(obd.commands.RPM, force=True)
        logging.debug("RPM value: %s", rpm.value)

        if rpm.value is None or rpm.value.magnitude == 0:
            logging.debug("RPM value is none or zero")
            engine_running = False
            logging.info("car is off")
            break

        logging.debug("RPM value: " + rpm.value)
        logging.info("getting car data...")
        
        sensor_data = []

        for sensor in SENSORS:
            logging.debug(f"reading {sensor}:")
            res = obd_connection.query(getattr(obd.commands, sensor))
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
        for i in range(0,10):
            logging.debug("waiting %s seconds", i)
            time.sleep(1)
        


def connect_sql():
    logging.info("connecting to SQL...")
    conn = sqlite3.connect('obd_data.db')
    c = conn.cursor()
    query = " REAL, ".join(x for x in SENSORS) + " REAL)"
    query = "CREATE TABLE IF NOT EXISTS obd_data (timestamp TEXT, " + query
    logging.debug("creating table...")
    c.execute(query)
    return conn

def is_device_connected(mac_address):
    logging.debug("checking if the obd reader is already connected with bluetooth")
    try:
        # Run the hcitool con command to list all connected devices
        output = subprocess.check_output(["hcitool", "con"], text=True)
        logging.debug(output)
        # Check if the MAC address is in the output
        if mac_address in output:
            logging.debug(f"Device {mac_address} is connected.")
            return True
        else:
            logging.warning(f"Device {mac_address} is not connected.")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking Bluetooth connections: {e}")
        return False

def wait_for_obd_connection():
    logging.info("Waiting for OBD-II connection...")

    # Try to connect to the OBD-II adapter
    connection = None
    while connection is None or not connection.is_connected():
        try:
            logging.debug("connecting to obd scanner bluetooth...")

            if not is_device_connected(MAC_ADDR):
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

            if not check_rfcomm_bind():
                logging.debug("creating serial port")
                os.system(f"/bin/bash -c \"rfcomm bind hci0 {MAC_ADDR}\"")

            obd.logger.setLevel(obd.logging.DEBUG)
            logging.info("connecting with the obd class")
            connection = obd.OBD()  # Auto-connect to USB or Bluetooth OBD-II adapter
        except Exception as e:
            logging.error(f"Connection error: {e}")
        logging.warning("retry in 2 second")
        time.sleep(2)  # Wait before trying again

    logging.info("Connected to OBD-II adapter.")
    # Check if the car is on by querying a basic command like RPM
    logging.info("checking if the car is responding...")
    while True:
        response = connection.query(obd.commands.RPM)
        if response and response.value is not None:
            logging.debug("successful read rpm value from the car.")
            logging.debug("Car is on and connected")
            break
        else:
            logging.warning("OBD-II adapter connected, but car is off or not detected. Retrying...")
        logging.warning("re-checking in 2 seconds")
        time.sleep(2)  # Wait before checking again

    return connection


if __name__ == "__main__":
    sys.stderr = open("stderr_reader.log", "a")
    sys.stdout = open("stdout_reader.log", "a")
    logging.basicConfig(filename='01_reader.log', format='%(asctime)s: %(message)s',
                    level=logging.DEBUG)
    obd_connection = wait_for_obd_connection()
    logging.info("CONNECTION WITH OBD SUCCESSFUL")
    sql_connection = connect_sql()
    logging.info("CONNECTION WITH DATABASE SUCCESSFUL")
    gather_informations(obd_connection, sql_connection)

    logging.info("SHUTTING DOWN IN 30 SECONDS...")
    obd.connection.close()
    sql_connection.close()
    os.system("systemctl disable car_service.service")
    time.sleep(30)
    logging.info("SHUTTING DOWN NOW")
    os.system("shutdown -h now")

        
