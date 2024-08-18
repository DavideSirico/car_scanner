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
    for i in range(0,95):
        current_command = obd.commands[1][i]
        res = connection.query(current_command, force=True)
        print(i)
        print(res.value)


def decoder_transmission_actual_gear(messages):
    """ decoder for RPM messages """
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = obd.bytes_to_int(d)
    return v

def decoder_engine_fuel_rate(messages):
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = obd.bytes_to_int(d)
    return v

def decoder_odometer(messages):
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = obd.bytes_to_int(d)
    return v

transmission_actual_gear = obd.OBDCommand("Transmission Actual Gear",
               "Transmission Actual Gear",
               b"01A4",
               4,
               decoder_transmission_actual_gear)

engine_fuel_rate = obd.OBDCommand("Engine Fuel Rate",
               "Engine Fuel Rate",
               b"019D",
               4,
               decoder_engine_fuel_rate)

odometer = obd.OBDCommand("Odometer",
               "Odometer",
               b"01A6",
               4,
               decoder_odometer)



res = connection.query(transmission_actual_gear, force=True)
print("transmission_actual_gear")
print(res.value)

res = connection.query(engine_fuel_rate, force=True)
print("engine_fuel_rate")
print(res.value)

res = connection.query(odometer, force=True)
print("odometer")
print(res.value)
