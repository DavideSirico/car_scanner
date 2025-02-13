import subprocess
from Logger import Logger
from Led import Led

import obd

logging = Logger()


class OBD:
    def __init__(self, mac_address: str, led_blue: Led):
        self.mac_address = mac_address
        cmds = [
            f"rfcomm bind hci0 {self.mac_address}",
            "bluetoothctl power on",
            "bluetoothctl pairable on",
            "bluetoothctl agent on",
            "bluetoothctl default-agent",
        ]
        self.led_blue = led_blue
        for cmd in cmds:
            output = subprocess.run(cmd.split(), capture_output=True)
            if not (output.returncode == 0 or output.returncode == 1):
                logging.error(
                    f"{cmd} failed: {output.stderr.decode('utf-8')}, {output.stdout.decode('utf-8')},{output.returncode}"
                )

        self.obd_connection = None

    def connect_bluetooth(self):
        logging.info("Waiting for OBD-II connection...")
        try:
            self.led_blue.start_blinking(0.5)
            logging.debug("connecting to obd scanner bluetooth...")

            output = subprocess.run(
                ["bluetoothctl", "connect", self.mac_address], capture_output=True
            )
            if output.returncode != 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl connect failed: {output.stderr}")

            logging.debug("pairing")
            output = subprocess.run(
                ["bluetoothctl", "pair", self.mac_address], capture_output=True
            )
            if output.returncode != 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl pair failed: {output.stderr}")

            logging.debug("trusting")
            output = subprocess.run(
                ["bluetoothctl", "trust", self.mac_address], capture_output=True
            )
            if output.returncode != 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl trust failed: {output.stderr}")

            obd.logger.setLevel(obd.logging.DEBUG)
            logging.info("connecting with the obd class")

        except Exception as e:
            logging.error(f"Connection error: {e}")
        finally:
            self.led_blue.stop_blinking()

    def disconnect_bluetooth(self):
        try:
            logging.debug("disconnecting from obd scanner bluetooth...")
            output = subprocess.run(
                ["bluetoothctl", "disconnect", self.mac_address], capture_output=True
            )
            if output.returncode != 0 and output.stderr is not None:
                logging.warning(f"bluetoothctl disconnect failed: {output.stderr}")
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return None
        finally:
            self.led_blue.turn_off()

    def connect_obd(self):
        try:
            self.led_blue.start_blinking(0.5)
            logging.info("connecting with the obd class")
            self.obd_connection = obd.OBD("/dev/rfcomm0")
        except Exception as e:
            logging.error(f"Connection error: {e}")
        finally:
            self.led_blue.stop_blinking()

    def status(self):
        if self.obd_connection is None:
            return False
        return self.obd_connection.status()

    def disconnect_obd(self):
        try:
            logging.info("disconnecting with the obd class")
            if self.obd_connection is not None:
                self.obd_connection.close()
        except Exception as e:
            logging.error(f"Connection error: {e}")
        finally:
            self.led_blue.turn_off()

    def is_connected(self):
        if self.obd_connection is None:
            return False
        return self.obd_connection.is_connected()

    def query(self, command):
        if self.obd_connection is not None and self.obd_connection.is_connected():
            return self.obd_connection.query(command, force=True)
        else:
            return None
