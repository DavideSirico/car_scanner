import threading
import time
import subprocess
import json
import math
import gpiozero

from Car import Car
from OBD import OBD
from DB import DB
from Led import Led
from CalculatedValues import CalculatedValues
from Logger import Logger


logger = Logger()
stop_event = threading.Event()

def monitoring(
    car: Car,
    obd_conn: OBD,
    db: DB,
    scanning_interval: float,
    calculatedValues: CalculatedValues,
    sensors_values: dict,
    led_blue: Led
):
    while not stop_event.is_set():
        # check if the car is on and the obd is connected, start monitoring the sensors every 10 seconds
        logger.debug("checking if the car is on and the obd is connected")

        if car.is_car_on() and obd_conn.is_connected():
            logger.debug("car is on and obd is connected")

            led_blue.turn_on()
            logger.debug("read sensors")

            sensors_values = car.read_sensors(sensors_values)
            logger.debug("insert data into the db")
            
            maf = sensors_values["MAF"]
            speed = sensors_values["SPEED"]
            rpm = sensors_values["RPM"]
            calculated_values = calculatedValues.calculate_values(maf,speed,rpm)
            for calculated_value in calculated_values:
                logger.debug(f"{calculated_value}: {calculated_values[calculated_value]}")

            
            db.insert_data_sensors(sensors_values, calculated_values)
            logger.debug("wait")

            if not db._connected_to_wifi():
                db.led_green.turn_off()
            else:
                db.led_green.turn_on()

            time.sleep(scanning_interval)
        else:
            time.sleep(5)
            # if the car is off but the obd is connected, disconnect the obd to let it sleep
            if obd_conn.is_connected() and not car.is_car_on():
                logger.debug("car is off and obd is connected")
                obd_conn.disconnect_obd()
                obd_conn.disconnect_bluetooth()
                logger.debug("obd is disconnected")

            # the the car is off and the obd is disconnected try every 5 minutes to reconnect
            while not obd_conn.is_connected() and not car.is_car_on():
                logger.debug("waiting 300 seconds")

                time.sleep(300)
                logger.debug("car is off and obd is disconnected")
                
                logger.debug("send data to server")
                db.send_wifi_db()

                led_blue.turn_off()
                if not stop_event.is_set():
                    logger.debug("try to reconnect")

                    obd_conn.connect_bluetooth()
                    obd_conn.connect_obd()
                    logger.debug("obd is connected")

                else:
                    return
        logger.debug("main loop waiting")
def shutdown(switch_pin: int):
    # check switch status
    # switch = gpiozero.Button(switch_pin)
    # switch.wait_for_press()
    logger.info("button pressed")
    stop_event.set()


def load_config(filename):
    with open(filename, "r") as file:
        return json.load(file)


def main():
    # Load the configuration
    config = load_config("config.json")

    # Access configuration values
    SCANNING_INTERVAL = config["SCANNING_INTERVAL"]
    SENSORS = config["SENSORS"]
    MAC_ADDR = config["MAC_ADDR"]

    server_properties = dict()
    server_properties["SERVER_ADDR"] = config["SERVER_ADDR"]
    server_properties["SERVER_DB_PATH"] = config["SERVER_DB_PATH"]
    server_properties["LOCAL_DB_PATH"] = config["LOCAL_DB_PATH"]
    server_properties["SERVER_USER"] = config["SERVER_USER"]

    LED_GREEN_PIN = config["LED_GREEN"]
    LED_RED_PIN = config["LED_RED"]
    LED_BLUE_PIN = config["LED_BLUE"]
    SWITCH_PIN = config["SWITCH"]
    CALCULATED_VALUES = config["CALCULATED_VALUES"]
    CAR_PROPERTIES = config["CAR_PROPERTIES"]
    sensors_values = dict.fromkeys(SENSORS, None)

    # inizialize the leds
    led_red = Led(LED_RED_PIN, "red", 0.5)
    led_green = Led(LED_GREEN_PIN, "green", 1)
    led_blue = Led(LED_BLUE_PIN, "blue", 0.15)

    # initialize the main objects
    calculatedValues = CalculatedValues(CALCULATED_VALUES, CAR_PROPERTIES)
    db = DB(server_properties, SENSORS, CALCULATED_VALUES, led_green)
    obd_conn = OBD(MAC_ADDR, led_blue)
    car = Car(obd_conn, led_blue)

    global stop_event
    stop_event = threading.Event()

    monitoring_thread = threading.Thread(
        target=monitoring,
        args=(
            car,
            obd_conn,
            db,
            SCANNING_INTERVAL,
            calculatedValues,
            sensors_values,
            led_blue
        ),
    )
    # shutdown_thread = threading.Thread(target=shutdown, args=(SWITCH,))

    switch = gpiozero.Button(SWITCH_PIN)
    switch.when_released = shutdown
    monitoring_thread.start()
    # shutdown_thread.start()

    led_red.turn_on()

    monitoring_thread.join()
    # shutdown_thread.join()

    db.connection.close()
    obd_conn.disconnect_obd()
    obd_conn.disconnect_bluetooth()
    led_red.turn_off()
    led_green.turn_off()
    led_blue.turn_off()

    logger.info("END OF PROGRAM")
    subprocess.run(["shutdown", "-h", "now"])

if __name__ == "__main__":
    main()
