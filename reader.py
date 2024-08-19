# sistema di soft-shutdown
# sistema di raccolta dati in formato prometheus?? o json/xml (servizio)
# script durante l'avvio
# collegamento all'obd
# sistema di logging
# gestione delle eccezioni
# controllare se sono a casa (collegato al wifi) e mandare i dati a 192.168.1.100


# 1. collegamento all'obd
import subprocess
import os
import obd
import time
import socket
import sqlite3

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
    obd_mac_addr = "13:E0:2F:8D:54:A9"

 #   os.system("/bin/bash -c \"bluetoothctl power on\"")
 #   os.system("/bin/bash -c \"bluetoothctl pairable on\"")
    os.system("/bin/bash -c \"bluetoothctl agent on\"")
    os.system("/bin/bash -c \"bluetoothctl default-agent\"")
    # se il pairing e' gia stato effettuato va in loop FIXME
    # os.system(f"/bin/bash -c \"bluetoothctl connect {obd_mac_addr}\"")
    os.system(f"/bin/bash -c \"bluetoothctl pair {obd_mac_addr}\"")
    # os.system(f"/bin/bash -c \"bluetoothctl trust {obd_mac_addr}\"")
    os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")


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
        engine_load = obd_connection.query(obd.commands.ENGINE_LOAD, force=True)
        if engine_load.is_null():
            engine_load.value = -1
        coolant_temp = obd_connection.query(obd.commands.COOLANT_TEMP, force=True)
        if coolant_temp.is_null():
            coolant_temp.value = -1

        fuel_pressure = obd_connection.query(obd.commands.FUEL_PRESSURE, force=True)
        if fuel_pressure.is_null():
            fuel_pressure.value = -1
        intake_pressure = obd_connection.query(obd.commands.INTAKE_PRESSURE, force=True)
        if intake_pressure.is_null():
            intake_pressure.value = -1
        speed = obd_connection.query(obd.commands.SPEED, force=True)
        if speed.is_null():
            speed.value = -1
        intake_temp = obd_connection.query(obd.commands.INTAKE_TEMP, force=True)
        if intake_temp.is_null():
            intake_temp.value = -1
        maf = obd_connection.query(obd.commands.MAF, force=True)
        if maf.is_null():
            maf.value = -1
        throttle_pos = obd_connection.query(obd.commands.THROTTLE_POS, force=True)
        if throttle_pos.is_null():
            throttle_pos.value = -1
        engine_run_time = obd_connection.query(obd.commands.RUN_TIME, force=True)
        if engine_run_time.is_null():
            engine_run_time.value = -1
        fuel_level = obd_connection.query(obd.commands.FUEL_LEVEL, force=True)
        if fuel_level.is_null():
            fuel_level.value = -1
        catalyst_temp_0_0 = obd_connection.query(obd.commands.CATALYST_TEMP_B1S1, force=True)
        if catalyst_temp_0_0.is_null():
            catalyst_temp_0_0.value = -1
        catalyst_temp_0_1 = obd_connection.query(obd.commands.CATALYST_TEMP_B2S1, force=True)
        if catalyst_temp_0_1.is_null():
            catalyst_temp_0_1.value = -1
        catalyst_temp_1_0 = obd_connection.query(obd.commands.CATALYST_TEMP_B1S2, force=True)
        if catalyst_temp_1_0.is_null():
            catalyst_temp_1_0.value = -1
        catalyst_temp_1_1 = obd_connection.query(obd.commands.CATALYST_TEMP_B2S2, force=True)
        if catalyst_temp_1_1.is_null():
            catalyst_temp_1_1.value = -1
        relative_throttle_pos = obd_connection.query(obd.commands.RELATIVE_THROTTLE_POS, force=True)
        if relative_throttle_pos.is_null():
            relative_throttle_pos.value = -1
        ambient_air_temp = obd_connection.query(obd.commands.AMBIANT_AIR_TEMP, force=True)
        if ambient_air_temp.is_null():
            ambient_air_temp.value = -1
        relative_accel_pos = obd_connection.query(obd.commands.RELATIVE_ACCEL_POS, force=True)
        if relative_accel_pos.is_null():
            relative_accel_pos.value = -1
        fuel_rate = obd_connection.query(obd.commands.FUEL_RATE, force=True)
        if fuel_rate.is_null():
            fuel_rate.value = -1

        print("saving data")

        sql_connection.execute("INSERT INTO obd_data (timestamp, engine_load, coolant_temp, fuel_pressure, intake_pressure, rpm, speed, intake_temp, maf, throttle_pos, engine_run_time, fuel_level, catalyst_temp_0_0, catalyst_temp_0_1, catalyst_temp_1_0, catalyst_temp_1_1, relative_throttle_pos, ambient_air_temp, relative_accel_pos, fuel_rate) VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (engine_load.value, coolant_temp.value, fuel_pressure.value, intake_pressure.value, rpm.value, speed.value, intake_temp.value, maf.value, throttle_pos.value, engine_run_time.value, fuel_level.value, catalyst_temp_0_0.value, catalyst_temp_0_1.value, catalyst_temp_1_0.value, catalyst_temp_1_1.value, relative_throttle_pos.value, ambient_air_temp.value, relative_accel_pos.value, fuel_rate))
        sql_connection.commit()
        print("\n------------------\n")
        time.sleep(10)


def is_car_on(connection):
    if connection.status() == obd.OBDStatus.CAR_CONNECTED:
        return True
    return False

def connect_sql():
    print("connecting to sql...")
    conn = sqlite3.connect('obd_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS obd_data (timestamp TEXT, engine_load REAL, coolant_temp REAL, fuel_pressure REAL, intake_pressure REAL, rpm REAL, speed REAL, intake_temp REAL, maf REAL, throttle_pos REAL, engine_run_time REAL, fuel_level REAL, \
                           catalyst_temp_0_0 REAL, catalyst_temp_0_1 REAL, catalyst_temp_1_0 REAL, catalyst_temp_1_1 REAL, relative_throttle_pos REAL, ambient_air_temp REAL, relative_accel_pos, fuel_rate)''')
    return conn


def wait_for_obd_connection():
    print("Waiting for OBD-II connection...")

    # Try to connect to the OBD-II adapter
    connection = None
    while connection is None or not connection.is_connected():
        try:
            # TODO check if it is aldready connected
            print("connecting...")
            obd_mac_addr = "13:E0:2F:8D:54:A9"

            #os.system("/bin/bash -c \"bluetoothctl power on\"")
            #os.system("/bin/bash -c \"bluetoothctl pairable on\"")
            #os.system("/bin/bash -c \"bluetoothctl agent on\"")
            #os.system("/bin/bash -c \"bluetoothctl default-agent\"")
            # se il pairing e' gia stato effettuato va in loop FIXME
            # os.system(f"/bin/bash -c \"bluetoothctl connect {obd_mac_addr}\"")
            #os.system(f"/bin/bash -c \"bluetoothctl pair {obd_mac_addr}\"")
            # os.system(f"/bin/bash -c \"bluetoothctl trust {obd_mac_addr}\"")
<<<<<<< HEAD
            #os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")
            obd.logger.setLevel(obd.logging.DEBUG)
=======
            # TODO check
            os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")
>>>>>>> b22f75b929c29cfae721793a295aab03b9d84d24
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

        
