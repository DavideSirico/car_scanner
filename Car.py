import logging

from Led import Led
from OBD import OBD

import obd

class Car:
    def __init__(self, obd_connection: OBD, led_blue: Led):
        self.obd_connection = obd_connection
        self.led_blue = led_blue

    def is_car_on(self):
        try:
            if self.obd_connection is not None and self.obd_connection.is_connected():
                logging.info("checking if the car is responding...")
                response = self.obd_connection.query(obd.commands.RPM)
                if response is not None and response.value is not None:
                    self.led_blue.turn_on()
                    logging.debug("Car is on and connected")
                    return True
                logging.debug("Car is not responding")
            else:
                logging.debug("OBD connection is not connected")
                self.led_blue.turn_off()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        
        return False
    def read_sensor(self, sensor: str):
        logging.debug(f"reading {sensor}:")
        res = self.obd_connection.query(getattr(obd.commands, sensor))
        if res.value is not None: 
            logging.debug(res.value.magnitude)
        return res
    
    def read_sensors(self, sensors: list):
        sensor_data = []

        for sensor in sensors:
            res = self.read_sensor(sensor)        
            if res.value is not None: 
                sensor_data.append(res.value.magnitude)
            else:
                sensor_data.append(None)

        return sensor_data
