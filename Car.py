from Logger import Logger

from Led import Led
from OBD import OBD

import obd

logger = Logger()


class Car:
    def __init__(self, obd_connection: OBD, led_blue: Led):
        self.obd_connection = obd_connection
        self.led_blue = led_blue

    def is_car_on(self):
        try:
            if self.obd_connection is not None and self.obd_connection.is_connected():
                logger.info("checking if the car is responding...")
                response = self.obd_connection.query(obd.commands.RPM)
                if response is not None and response.value is not None:
                    self.led_blue.turn_on()
                    logger.debug("Car is on and connected")
                    return True
                logger.debug("Car is not responding")
            else:
                logger.debug("OBD connection is not connected")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

        self.led_blue.turn_off()
        logger.info("Car is off or not connected")
        return False

    def read_sensor(self, sensor: str):
        logger.debug(f"reading {sensor}:")
        res = self.obd_connection.query(getattr(obd.commands, sensor))
        if res.value is not None:
            logger.debug(res.value.magnitude)
        return res

    def read_sensors(self, sensors: dict):
        for sensor in sensors:
            res = self.read_sensor(sensor)
            if res.value is not None:
                sensors[sensor] = res.value.magnitude
            else:
                sensors[sensor] = None

        return sensors
