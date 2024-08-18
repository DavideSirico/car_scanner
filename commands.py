import obd
import time
import sys

with open('file-commands.3', 'w') as sys.stdout:

    obd.logger.setLevel(obd.logging.DEBUG)
    ports = obd.scan_serial()      # return list of valid USB or RF ports
    print(ports)

    connection = obd.OBD()

    print("Connection status: ")
    print(connection.status())
    # mode 01
    print("mode 01")
    for i in range(0,201):
        current_command = obd.commands[1][i]
        res = connection.query(current_command, force=True)
        print(i)
        print(res.value)
