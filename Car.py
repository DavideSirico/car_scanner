from logger_config import setup_logger

from Led import Led
from OBD import OBD

import obd

logging, file_handler = setup_logger()
class Car:
    def __init__(self, obd_connection: OBD, led_blue: Led):
        self.obd_connection = obd_connection
        self.led_blue = led_blue
        
    def is_car_on(self):
        try:
            if self.obd_connection is not None and self.obd_connection.is_connected():
                logging.info("checking if the car is responding...")
                file_handler.flush()
                response = self.obd_connection.query(obd.commands.RPM)
                if response is not None and response.value is not None:
                    self.led_blue.turn_on()
                    logging.debug("Car is on and connected")
                    file_handler.flush()
                    return True
                logging.debug("Car is not responding")
                file_handler.flush()
            else:
                logging.debug("OBD connection is not connected")
                file_handler.flush()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            file_handler.flush()
        
        self.led_blue.turn_off()
        return False
    def read_sensor(self, sensor: str):
        logging.debug(f"reading {sensor}:")
        file_handler.flush()
        res = self.obd_connection.query(getattr(obd.commands, sensor))
        if res.value is not None: 
            logging.debug(res.value.magnitude)
            file_handler.flush()
        return res
    
    def read_sensors(self, sensors: dict):
        for sensor in sensors:
            res = self.read_sensor(sensor)        
            if res.value is not None: 
                sensors[sensor] = res.value.magnitude
            else:
                sensors[sensor] = None

        return sensors