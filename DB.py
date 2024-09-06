import logging
import subprocess
import threading

import sqlite3

class DB:
    def __init__(self, db_path: str, sensors: list):
        logging.info("connecting to SQL...")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = " REAL, ".join(x for x in self.sensors) + " REAL)"
        query = "CREATE TABLE IF NOT EXISTS obd_data (timestamp DATE DEFAULT (datetime('now','localtime')), " + query
        logging.debug("creating table...")
        c.execute(query)
        logging.info("CONNECTION WITH DATABASE SUCCESSFUL")
        self.connection = conn
        self.db_path = db_path
        self.lock = threading.Lock()
        self.sensors = sensors
    
    def send_db(self, server_addr: str, server_db_path: str, server_user: str):
        with self.lock:    
            logging.debug("sending database to server...")
            try:
                output = subprocess.run(["scp", self.db_path, f"{server_user}@{server_addr}:{server_db_path}"], capture_output=True)
                if output.returncode != 0:
                    logging.error(f"Failed to send data: {output.stderr.decode('utf-8')}")
                    return
                logging.info("Data sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send data: {e}")

    def insert_data_sensors(self, sensors_data: list):
        with self.lock:
            try:
                logging.info("saving data")
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO obd_data (timestamp, " + ", ".join(self.sensors) + ") VALUES (datetime('now'), " + ", ".join(["?"] * len(self.sensors)) + ")", sensors_data
                )
                self.connection.commit()
                logging.info("data saved")
            except Exception as e:
                logging.error(f"Failed to save data: {e}")
        
