import obd
import time
import sys
import os

def decoder_transmission_actual_gear(messages):
    """ decoder for RPM messages """
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = obd.utils.bytes_to_int(d)
    return v

def decoder_engine_fuel_rate(messages):
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = obd.utils.bytes_to_int(d)
    return v

def decoder_odometer(messages):
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = obd.utils.bytes_to_int(d)
    return v


with open('supported', 'w') as sys.stdout:
    obd_mac_addr = "13:E0:2F:8D:54:A9"
    os.system(f"/bin/bash -c \"rfcomm bind hci0 {obd_mac_addr}\"")

    obd.logger.setLevel(obd.logging.DEBUG)
    ports = obd.scan_serial()      # return list of valid USB or RF ports
    print(ports)

    connection = obd.OBD()

    print("Connection status: ")
    print(connection.status())
    """
    transmission_actual_gear = obd.OBDCommand("Transmission Actual Gear",
               "Transmission Actual Gear",
               b"01A4",
               4,
               decoder_transmission_actual_gear,
               obd.protocols.ECU.ALL
               )

    engine_fuel_rate = obd.OBDCommand("Engine Fuel Rate",
                "Engine Fuel Rate",
                b"019D",
                4,
                decoder_engine_fuel_rate,
                obd.protocols.ECU.ALL
                )

    odometer = obd.OBDCommand("Odometer",
                "Odometer",
                b"01A6",
                4,
                decoder_odometer,
                obd.protocols.ECU.ALL
                )



    res = connection.query(transmission_actual_gear, force=True)
    print("transmission_actual_gear")
    print(res.value)

    res = connection.query(engine_fuel_rate, force=True)
    print("engine_fuel_rate")
    print(res.value)

    res = connection.query(odometer, force=True)
    print("odometer")
    print(res.value)
"""
    res = connection.query(obd.commands.PIDS_A, force=True)
    print("supported pids")
    print("message:", end=" ") 
    print(res.messages)
    print("value:", end=" ")
    print(res.value)
    res = connection.query(obd.commands.PIDS_B, force=True)
    print("supported pids")
    print("message:", end=" ") 
    print(res.messages)
    print("value:", end=" ")
    print(res.value)
    res = connection.query(obd.commands.PIDS_C, force=True)
    print("supported pids")
    print("message:", end=" ") 
    print(res.messages)
    print("value:", end=" ")
    print(res.value)
    