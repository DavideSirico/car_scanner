# sistema di soft-shutdown
# sistema di raccolta dati in formato prometheus?? o json/xml (servizio)
# script durante l'avvio
# collegamento all'obd
# sistema di logging
# gestione delle eccezioni
# controllare se sono a casa (collegato al wifi) e mandare i dati a 192.168.1.100


# 1. collegamento all'obd
import os
import obd
import time
import socket
import sqlite3
import subprocess
import json 

SENSORS = ["ENGINE_LOAD", "COOLANT_TEMP", "FUEL_PRESSURE", "INTAKE_PRESSURE", "SPEED", "INTAKE_TEMP", "MAF", "THROTTLE_POS", "RUN_TIME", "FUEL_LEVEL", "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CATALYST_TEMP_B1S2", "CATALYST_TEMP_B2S2", "RELATIVE_THROTTLE_POS", "AMBIANT_AIR_TEMP", "RELATIVE_ACCEL_POS", "FUEL_RATE"]
MAC_ADDR = "13:E0:2F:8D:54:A9"

def check_rfcomm_bind():
    try:
        # Running the rfcomm show command
        output = subprocess.check_output(["rfcomm"], text=True)
        
        # Checking if hci0 is mentioned in the output
        if MAC_ADDR in output:
            print("RFCOMM bind to hci0 found.")
            return True
        else:
            print("No RFCOMM bind to hci0 found.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking RFCOMM: {e}")
        return False

def is_bluetooth_service_running():
    try:
        # Try checking the service status using systemctl
        output = subprocess.check_output(['systemctl', 'is-active', 'bluetooth'], text=True)
        return output.strip() == 'active'
    except subprocess.CalledProcessError:
        # Handle the case where systemctl is not available or service is inactive
        return False

def is_root():
    if os.geteuid() == 0:
        return True
    return False


def connect_obd():
    # check if the bluetooth service is running
    if not is_bluetooth_service_running():
        print("bluetooth")
        return -1 # Error
    if not is_root():
        print("root")
        return -1
    
    # IOS
    # obd_mac_addr = "D2:E0:2F:8D:54:A9"
    # Android

 #   os.system("/bin/bash -c \"bluetoothctl power on\"")
 #   os.system("/bin/bash -c \"bluetoothctl pairable on\"")
    os.system("/bin/bash -c \"bluetoothctl agent on\"")
    os.system("/bin/bash -c \"bluetoothctl default-agent\"")
    # se il pairing e' gia stato effettuato va in loop FIXME
    # os.system(f"/bin/bash -c \"bluetoothctl connect {MAC_ADDR}\"")
    os.system(f"/bin/bash -c \"bluetoothctl pair {MAC_ADDR}\"")
    # os.system(f"/bin/bash -c \"bluetoothctl trust {MAC_ADDR}\"")
    os.system(f"/bin/bash -c \"rfcomm bind hci0 {MAC_ADDR}\"")


    obd.logger.setLevel(obd.logging.DEBUG)
    ports = obd.scan_serial()      # return list of valid USB or RF ports
    print(ports)

    connection = obd.OBD()

    print("Connection status: ")
    print(connection.status())
    return connection

def gather_informations(obd_connection, sql_connection):
    print("Monitoring car engine status...")
    engine_running = True
    # mode 1
    while engine_running:
        print("checking if the car is still on")
        rpm = obd_connection.query(obd.commands.RPM, force=True)
        if rpm.value is None or rpm.value == 0:
            engine_running = False
            print("car is off")
            break
        print("getting car data...")
        
        sensor_data = []

        for sensor in SENSORS:
            print(f"reading {sensor}:")
            res = obd_connection.query(getattr(obd.commands, sensor))
            print(res.value.magnitude)
            sensor_data.append(res.value.magnitude)

        print("saving data")
        sql_connection.execute("INSERT INTO obd_data " + json.dumps(sensor_data) + ";"
        # sql_connection.execute("INSERT INTO obd_data (timestamp, engine_load, coolant_temp, fuel_pressure, intake_pressure, rpm, speed, intake_temp, maf, throttle_pos, engine_run_time, fuel_level, catalyst_temp_0_0, catalyst_temp_0_1, catalyst_temp_1_0, catalyst_temp_1_1, relative_throttle_pos, ambient_air_temp, relative_accel_pos, fuel_rate) VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (engine_load.value.magnitude, coolant_temp.value.magnitude, fuel_pressure.value.magnitude, intake_pressure.value.magnitude, rpm.value.magnitude, speed.value.magnitude, intake_temp.value.magnitude, maf.value.magnitude, throttle_pos.value.magnitude, engine_run_time.value.magnitude, fuel_level.value.magnitude, catalyst_temp_0_0.value.magnitude, catalyst_temp_0_1.value.magnitude, catalyst_temp_1_0.value.magnitude, catalyst_temp_1_1.value.magnitude, relative_throttle_pos.value.magnitude, ambient_air_temp.value.magnitude, relative_accel_pos.value.magnitude, fuel_rate.value.magnitude))
        sql_connection.commit()
        print("\n------------------\n")
        for i in range(0,10):
            print("sleeping...")
            time.sleep(1)


def is_car_on(connection):
    if connection.status() == obd.OBDStatus.CAR_CONNECTED:
        return True
    return False

def connect_sql():
    print("connecting to sql...")
    conn = sqlite3.connect('obd_data.db')
    c = conn.cursor()
    query = " REAL, ".join(x for x in SENSORS)
    query = query + " REAL)"
    query = "CREATE TABLE IF NOT EXISTS obd_data (timestamp TEXT, " + query
    c.execute(query)
    return conn

def is_device_connected(mac_address):
    try:
        # Run the hcitool con command to list all connected devices
        output = subprocess.check_output(["hcitool", "con"], text=True)
        print(output)
        # Check if the MAC address is in the output
        if mac_address in output:
            print(f"Device {mac_address} is connected.")
            return True
        else:
            print(f"Device {mac_address} is not connected.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking Bluetooth connections: {e}")
        return False

def wait_for_obd_connection():
    print("Waiting for OBD-II connection...")

    # Try to connect to the OBD-II adapter
    connection = None
    while connection is None or not connection.is_connected():
        try:
            print("connecting...")
            obd_mac_addr = "13:E0:2F:8D:54:A9"
            # TODO non va
            if not is_device_connected(obd_mac_addr):
                os.system("/bin/bash -c \"bluetoothctl power on\"")
                os.system("/bin/bash -c \"bluetoothctl pairable on\"")
                os.system("/bin/bash -c \"bluetoothctl agent on\"")
                os.system("/bin/bash -c \"bluetoothctl default-agent\"")
                # se il pairing e' gia stato effettuato va in loop FIXME
                os.system(f"/bin/bash -c \"bluetoothctl connect {obd_mac_addr}\"")
                os.system(f"/bin/bash -c \"bluetoothctl pair {obd_mac_addr}\"")
                os.system(f"/bin/bash -c \"bluetoothctl trust {obd_mac_addr}\"")

            if not check_rfcomm_bind():
                os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")

            obd.logger.setLevel(obd.logging.DEBUG)
            connection = obd.OBD()  # Auto-connect to USB or Bluetooth OBD-II adapter
        except Exception as e:
            print(f"Connection error: {e}")
        time.sleep(2)  # Wait before trying again

    print("Connected to OBD-II adapter.")

    # Check if the car is on by querying a basic command like RPM
    print("checking if the car is responding...")
    while True:
        response = connection.query(obd.commands.RPM)
        if response and response.value is not None:
            print("Car is on and connected.")
            break
        else:
            print("OBD-II adapter connected, but car is off or not detected. Retrying...")
        time.sleep(2)  # Wait before checking again

    return connection



if __name__ == "__main__":
    obd_connection = wait_for_obd_connection()
    sql_connection = connect_sql()
    gather_informations(obd_connection, sql_connection)
    time.sleep(30)
    print("shutting down...")
    os.system("shutdown -h now")

        
