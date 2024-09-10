# Car Scanner Project - README

## Project Overview

The **Car Scanner** project aims to provide a solution for reading and monitoring OBD-II (On-Board Diagnostics) data from a vehicle, log the data in a local SQLite database, and periodically send it to a remote server. The system also uses LED indicators to provide feedback on the vehicle's connection status and operations. The software is designed to run as a systemd service on a Linux-based environment.

### Key Features:
- OBD-II data collection and logging
- LED feedback system (Blue, Red, Green)
- SQLite database to store sensor data
- Remote server data upload via SCP
- Gear estimation from RPM and speed
- Automatic reconnection to OBD and Bluetooth

## Components

### 1. **Systemd Service: `car_scanner.service`**
The service is designed to run the main Python script (`main.py`) automatically as a background service on system startup. It ensures that the service restarts on failure.

**Key configurations:**
- Working directory: `/home/david/car_scanner`
- Python virtual environment: `/home/david/car_scanner/.venv`
- The service restarts on failure and runs in the background.

### 2. **Main Python Components:**
#### 1. `Car.py`:
Handles the OBD-II connection to the vehicle and performs sensor queries. It also provides methods for determining if the car is on and reading sensor data.

#### 2. `DB.py`:
Manages the local SQLite database and handles inserting sensor data into the database. It also manages sending the database file to a remote server when connected to Wi-Fi.

#### 3. `Led.py`:
Controls the LED indicators (Red, Green, and Blue). The LEDs provide visual feedback on system status, such as connection states and data transmission.

#### 4. `main.py`:
The main entry point of the system. It loads configuration settings, initializes components, and starts monitoring the OBD-II data. It also controls the logic for detecting whether the car is on and initiates data logging, transmission, and sensor monitoring.

#### 5. `OBD.py`:
Responsible for managing the Bluetooth connection to the OBD-II scanner and querying the OBD-II sensors for data.

### 3. **Configuration File: `config.json`**
The configuration file holds critical settings for the system, such as:
- Scanning interval
- List of sensors to monitor
- Bluetooth MAC address of the OBD-II scanner
- Remote server details for data upload
- LED pin mappings and other hardware-related settings

### 4. **Database**
An SQLite database (`obd_data.db`) is created locally, storing the OBD sensor data in a structured format. The table columns are dynamically created based on the sensors listed in the configuration.

### 5. **Gear Estimation**
`main.py` contains a method to estimate the current gear based on the vehicle's speed, RPM, and tire radius.

### 6. **Requirements: `requirements.txt`**
The Python dependencies for the project, including OBD-II libraries, GPIO control, and SQLite, are specified here.

## Installation

### 1. Clone the repository:
```bash
git clone https://github.com/yourusername/car_scanner.git
cd car_scanner
```

### 2. Set up the Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the project:
Edit the `config.json` file to match your hardware and server setup. Ensure that the MAC address of your OBD-II scanner and other settings (e.g., gear ratios, LED pin numbers) are correct.

### 4. Install the systemd service:
```bash
sudo cp car_scanner.service /etc/systemd/system/
sudo systemctl enable car_scanner.service
sudo systemctl start car_scanner.service
```

### 5. View Logs:
You can check the service logs using:
```bash
journalctl -u car_scanner.service
```

## Usage

Once installed and running, the system will automatically start collecting OBD-II data when the car is turned on. Data will be saved locally and transmitted to the remote server periodically. LEDs will provide status feedback:
- **Blue LED**: Indicates OBD-II connection status.
- **Green LED**: Blinks during data transmission.
- **Red LED**: Indicates system status (active when the system is running).

## Shutdown Procedure
A physical switch connected to a GPIO pin (specified in `config.json`) allows the system to gracefully shut down when released.

## To-Do List
- Improve LED intensity control
- Handle database errors more gracefully
- Refactor the gear estimation function into a class method

---

This project is still in progress, and contributions or suggestions are welcome.
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTg0MDYwMDEwXX0=
-->