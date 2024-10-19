from logger_config import setup_logger
import threading
import time
import subprocess 
import json 
import math

from Car import Car
from OBD import OBD
from DB import DB
from Led import Led

import gpiozero

logger, file_handler = setup_logger()
stop_event = threading.Event()

def estimate_gear(speed, rpm, tire_radius, gear_ratios):
    # Ensure that inputs are in the correct data type
    try:
        speed = float(speed)
        rpm = float(rpm)
        tire_radius = float(tire_radius)
        gear_ratios = [float(gr) for gr in gear_ratios]
    except ValueError:
        raise ValueError("All inputs (speed, rpm, tire_radius, gear_ratios) must be numbers.")
    
    # Convert speed from km/h to m/s
    speed_m_s = speed * (1000.0 / 3600.0)
    
    # Avoid division by zero in case speed is zero
    if speed_m_s == 0:
        raise ValueError("Speed cannot be zero.")

    # Calculate the gear ratio
    gear_ratio = (rpm * tire_radius * 2.0 * math.pi) / (speed_m_s * 60.0)
    
    # Find the closest matching gear ratio from known gear ratios
    closest_gear = min(gear_ratios, key=lambda x: abs(x - gear_ratio))
    
    return gear_ratios.index(closest_gear) + 1  # Return the gear number


def monitoring(car: Car, obd_conn: OBD, db: DB, scanning_interval: float, sensors: dict, led_blue: Led, TIRE_RADIUS: float, GEAR_RATIOS: list):
    while not stop_event.is_set():
        # check if the car is on and the obd is connected, start monitoring the sensors every 10 seconds
        logger.debug("checking if the car is on and the obd is connected")
        file_handler.flush()
        if car.is_car_on() and obd_conn.is_connected():
            logger.debug("car is on and obd is connected")
            file_handler.flush()
            led_blue.turn_on()
            logger.debug("read sensors")
            file_handler.flush()
            sensors = car.read_sensors(sensors)
            logger.debug("insert data into the db")
            file_handler.flush()

            rpm = sensors["rpm"]
            speed = sensors["speed"]

            estimated_gear = estimate_gear(speed, rpm, TIRE_RADIUS, GEAR_RATIOS)
            sensors["gear"] = estimated_gear
            db.insert_data_sensors(sensors)
            logger.debug("send data to server")
            file_handler.flush()
            db.send_wifi_db()
            logger.debug("wait")
            file_handler.flush()
            time.sleep(scanning_interval-1)
        else:
            # if the car is off but the obd is connected, disconnect the obd to let it sleep
            if obd_conn.is_connected():
                logger.debug("car is off and obd is connected")
                file_handler.flush()
                obd_conn.disconnect_obd()
                obd_conn.disconnect_bluetooth()
                logger.debug("obd is disconnected")
                file_handler.flush()
            # the the car is off and the obd is disconnected try every 5 minutes to reconnect
            while not obd_conn.is_connected() and not car.is_car_on():
                logger.debug("waiting 15 seconds")
                file_handler.flush()
                time.sleep(15)
                logger.debug("car is off and obd is disconnected")
                file_handler.flush()
                led_blue.turn_off()
                if not stop_event.is_set():
                    logger.debug("try to reconnect")
                    file_handler.flush()
                    obd_conn.connect_bluetooth()
                    obd_conn.connect_obd()
                    logger.debug("obd is connected")
                    file_handler.flush()
                else:
                    return
                
        logger.debug("main loop waiting")
        file_handler.flush()
        time.sleep(1)


def shutdown(switch_pin: int):
    # check switch status
    # switch = gpiozero.Button(switch_pin)
    # switch.wait_for_press()
    stop_event.set()

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def main():
    # Load the configuration
    config = load_config('config.json')


    # Access configuration values
    SCANNING_INTERVAL = config["SCANNING_INTERVAL"]
    SENSORS = config["SENSORS"]
    MAC_ADDR = config["MAC_ADDR"]

    server_properties = dict()
    server_properties["SERVER_ADDR"] = config["SERVER_ADDR"]
    server_properties["ROUTER_ADDR"] = config["ROUTER_ADDR"]
    server_properties["SERVER_DB_PATH"] = config["SERVER_DB_PATH"]
    server_properties["LOCAL_DB_PATH"] = config["LOCAL_DB_PATH"]
    server_properties["SERVER_USER"] = config["SERVER_USER"]

    LED_GREEN_PIN = config["LED_GREEN"]
    LED_RED_PIN = config["LED_RED"]
    LED_BLUE_PIN = config["LED_BLUE"]
    SWITCH_PIN = config["SWITCH"]
    TIRE_RADIUS = config["TIRE_RADIUS"]
    GEAR_RATIOS = config["GEAR_RATIOS"]
    CALCULATED_VALUES = config["CALCULATED_VALUES"]

    sensors = dict.fromkeys(SENSORS, None)


    # inizialize the leds
    led_red = Led(LED_RED_PIN, "red", 0.5)
    led_green = Led(LED_GREEN_PIN, "green", 1)
    led_blue = Led(LED_BLUE_PIN, "blue", 0.15)

    # initialize the main objects
    db = DB(server_properties, SENSORS, CALCULATED_VALUES, led_green)
    obd_conn = OBD(MAC_ADDR, led_blue)
    car = Car(obd_conn, led_blue)


    global stop_event
    stop_event = threading.Event()

    monitoring_thread = threading.Thread(target=monitoring, args=(car, obd_conn, db, SCANNING_INTERVAL, SENSORS, led_blue, TIRE_RADIUS, GEAR_RATIOS))
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
    file_handler.flush()
    subprocess.run(["shutdown", "-h", "now"])


if __name__ == "__main__":
    main()

# TODO:
# - intensity of the leds
# - db errors
# - refactor sensors list and sensors_data list in a single dictionary
# - refactor the estimate gear function and make it a method of a class
