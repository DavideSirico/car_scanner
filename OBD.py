import subprocess
import logging

import obd

class OBD:
    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        cmds = [
            f"rfcomm bind hci0 {self.mac_address}",
            "bluetoothctl power on",
            "bluetoothctl pairable on",
            "bluetoothctl agent on",
            "bluetoothctl default-agent"
        ]

        for cmd in cmds:
            output = subprocess.run(cmd.split(), capture_output=True)
            if output.returncode != 0:
                raise Exception(f"{cmd} failed: {output.stderr.decode('utf-8')}")

    def connect_bluetooth(self):
        logging.info("Waiting for OBD-II connection...")
        try:
            logging.debug("connecting to obd scanner bluetooth...")

            output = subprocess.run(["bluetoothctl", "connect", self.mac_address], capture_output=True)
            if output.returncode!= 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl connect failed: {output.stderr}")

            logging.debug("pairing")
            output = subprocess.run(["bluetoothctl", "pair", self.mac_address], capture_output=True)
            if output.returncode!= 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl pair failed: {output.stderr}")
            
            logging.debug("trusting")
            output = subprocess.run(["bluetoothctl", "trust", self.mac_address], capture_output=True)
            if output.returncode!= 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl trust failed: {output.stderr}")

            obd.logger.setLevel(obd.logging.DEBUG)
            logging.info("connecting with the obd class")

        except Exception as e:
            logging.error(f"Connection error: {e}")
    
    def disconnect_bluetooth(self):
        try:
            logging.debug("disconnecting from obd scanner bluetooth...")
            output = subprocess.run(["bluetoothctl", "disconnect", self.mac_address], capture_output=True)
            if output.returncode!= 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl disconnect failed: {output.stderr}")
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return None
    
    def connect_obd(self):
        try:
            logging.info("connecting with the obd class")
            self.obd_connection = obd.OBD("/dev/rfcomm0")
        except Exception as e:
            logging.error(f"Connection error: {e}")

    def status(self):
        return self.obd_connection.status()

    def disconnect_obd(self):
        try:
            logging.info("disconnecting with the obd class")
            self.obd_connection.close()
        except Exception as e:
            logging.error(f"Connection error: {e}")
