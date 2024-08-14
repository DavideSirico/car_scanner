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
    obd_mac_addr = "XX:XX:XX:XX:XX:XX"

    os.system("/bin/bash -c \"bluetoothctl power on\"")
    os.system("/bin/bash -c \"bluetoothctl pairable on\"")
    os.system("/bin/bash -c \"bluetoothctl agent on\"")
    os.system("/bin/bash -c \"bluetoothctl default-agent\"")
    os.system(f"/bin/bash -c \"bluetoothctl pair {obd_mac_addr}\"")
    os.system(f"/bin/bash -c \"bluetoothctl trust {obd_mac_addr}\"")
    os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")


    obd.logger.setLevel(obd.logging.DEBUG)
    ports = obd.scan_serial()      # return list of valid USB or RF ports
    print(ports)

    connection = obd.OBD()

    return connection.status()




if __name__ == "__main__":
    connect_obd()
