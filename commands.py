import obd
import time
import sys

with open('file-commands.2', 'w') as sys.stdout:

    obd.logger.setLevel(obd.logging.DEBUG)
    ports = obd.scan_serial()      # return list of valid USB or RF ports
    print(ports)

    connection = obd.OBD()

    print("Connection status: ")
    print(connection.status())


    # mode 01
    print("mode 01")
    for i in range(0,95):
        current_command = obd.commands[1][i]
        res = connection.query(current_command, force=True)
        print(i)
        print(res.value)

    # mode 02
    print("mode 02")
    for i in range(0,95):
        current_command = obd.commands[2][i]
        res = connection.query(current_command, force=True)
        print(i)
        print(res.value)

    # mode 03
    print("mode 03")
    current_command = obd.commands[3][0]
    res = connection.query(current_command, force=True)
    print(res.value)
    time.sleep(1)

    # mode 04
    print("mode 04")
    current_command = obd.commands[4][0]
    res = connection.query(current_command, force=True)
    print(res.value)
    time.sleep(1)

    # mode 06
    print("mode 06")
    for i in range(0,28):
        current_command = obd.commands[6][i]
        res = connection.query(current_command, force=True)
        print(i)
        print(res.value)


    # mode 07
    print("mode 07")
    current_command = obd.commands[7][0]
    res = connection.query(current_command, force=True)
    print(res.value)
    time.sleep(1)
    # mode 09
    print("mode 09")
    for i in range(0,12):
        current_command = obd.commands[9][i]
        res = connection.query(current_command, force=True)
        print(i)
        print(res.value)