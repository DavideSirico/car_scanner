# sistema di soft-shutdown
# sistema di raccolta dati in formato prometheus?? o json/xml (servizio)
# script durante l'avvio
# collegamento all'obd
# sistema di logging
# gestione delle eccezioni
# controllare se sono a casa (collegato al wifi) e mandare i dati a 192.168.1.100


# 1. collegamento all'obd


# echo -e "connect AA:BB:CC:DD:EE \nquit" | bluetoothctl

import subprocess
import os
import obd
import time
import socket

def is_bluetooth_service_running():
    try:
        # Try checking the service status using systemctl
        output = subprocess.check_output(['systemctl', 'is-active', 'bluetooth'], text=True)
        return output.strip() == 'active'
    except subprocess.CalledProcessError:
        # Handle the case where systemctl is not available or service is inactive
        return False

def connect_obd():
    # check if the bluetooth service is running
    if not is_bluetooth_service_running():
        return -1 # Error
    


    # connect to obd 
    obd_mac_addr = "D2:E0:2F:8D:54:A9"

    os.system("/bin/bash -c \"bluetoothctl power on\"")
    os.system("/bin/bash -c \"bluetoothctl pairable on\"")
    os.system("/bin/bash -c \"bluetoothctl agent on\"")
    os.system("/bin/bash -c \"bluetoothctl default-agent\"")
    # se il pairing e' gia stato effettuato va in loop FIXME
    os.system(f"/bin/bash -c \"bluetoothctl pair {obd_mac_addr}\"")
    os.system(f"/bin/bash -c \"bluetoothctl trust {obd_mac_addr}\"")
    os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")


    obd.logger.setLevel(obd.logging.DEBUG)
    ports = obd.scan_serial()      # return list of valid USB or RF ports
    print(ports)

    connection = obd.OBD()

    print("Connection status: ")
    print(connection.status())

# Print supported commands
    commands = connection.supported_commands
    print("Supported commands: ")
    with open("file.txt", "w") as f:
        for command in commands:
            print(command.name)
            f.write(command.name)

    # Send a command
    while True:
        command = input("Enter command (type 'quit' to exit): ")
        if (command == "quit"):
            break
        try:
            res = connection.query(obd.commands[command])
            print(res.value)
        except Exception as ex:
            print("Error: " + str(ex))

# Close the connection
    connection.close()

def gater_informations(connection):
    res = connection.query(obd.commands[command])


def is_wifi_connected():
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("192.168.1.100", "53"))
        return True
    except socket.error as ex:
        print(ex)
        return False


def send_data():
    # send data to 192.168.1.100 with all the data?
    pass


if __name__ == "__main__":
    connection = connect_obd()
    """
    while True:
        if is_car_on():
            gather_informations(connection)
            if is_wifi_connected():
                send_data()
            time.sleep(10)
        else:
            # shutdown the raspb
            os.system("shutdown -s")
    """

