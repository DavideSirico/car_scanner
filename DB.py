import logging
import subprocess
import threading

import sqlite3

from Led import Led
class DB:
    def __init__(self, server_properties: dict, sensors: dict, calculated_values: dict, led_green: Led):
        logging.info("Connecting to the SQL database...")
        
        # Store the provided parameters
        self.server_properties = server_properties
        self.calculated_values = calculated_values
        self.led_green = led_green
        
        # Initialize thread lock for concurrency
        self.lock = threading.Lock()

        # Establish a connection to the SQLite database
        try:
            self.connection = sqlite3.connect(self.server_properties["local_db_path"], check_same_thread=False)
            c = self.connection.cursor()

            # Create the table with dynamic sensor columns
            sensor_columns = ", ".join(f"{sensor} REAL" for sensor in sensors)
            calculated_values_columns = ", ".join(f"{value} REAL" for value in calculated_values)
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS obd_data (
                    timestamp DATE DEFAULT (datetime('now', 'localtime')),
                    {sensor_columns}
                    {calculated_values_columns}
                )
            """

            logging.debug("Creating table if not exists...")
            c.execute(create_table_query)
            logging.info("Database connection and table setup successful.")
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to the database: {e}")
    
    def _send_db(self):
        with self.lock:
            self.led_green.start_blinking(0.5)
            logging.debug("sending database to server...")
            try:
                output = subprocess.run(["scp", self.server_properties["db_path"], f"{self.server_properties["server_user"]}@{self.server_properties["server_addr"]}:{self.server_properties["server_db_path"]  }"], capture_output=True)
                if output.returncode != 0:
                    logging.error(f"Failed to send data: {output.stderr.decode('utf-8')}")
                    return
                logging.info("Data sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send data: {e}")
            finally:
                self.led_green.stop_blinking()
    def _connected_to_wifi(self):
        try:
            output = subprocess.run(["ping", "-c", "1", self.server_properties["server_addr"]], capture_output=True)
            if output.returncode == 0:
                return True
            return False
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return False

    def send_wifi_db(self):
        if self._connected_to_wifi():
            self.led_green.turn_on()
            self._send_db()
        else:
            self.led_green.turn_off()
    def insert_data_sensors(self, sensors: dict, calculated_values: dict):
        with self.lock:
            try:
                logging.info("Saving sensor and calculated data...")

                # Combine sensors and calculated values into a single dataset
                data_to_insert = list(sensors.values()) + list(calculated_values.values())

                # Prepare SQL query to insert data for both sensors and calculated values
                all_columns = list(sensors.keys()) + list(calculated_values.keys())
                placeholders = ", ".join(["?"] * len(all_columns))
                
                query = f"""
                    INSERT INTO obd_data (timestamp, {", ".join(all_columns)})
                    VALUES (datetime('now'), {placeholders})
                """

                # Execute the query with the combined data
                cursor = self.connection.cursor()
                cursor.execute(query, data_to_insert)
                self.connection.commit()

                logging.info("Data saved successfully.")
            except Exception as e:
                logging.error(f"Failed to save data: {e}")
            
