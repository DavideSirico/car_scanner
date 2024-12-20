# Car Scanner Project

## Project Overview
This project is made to collect, display and analyze information about your car and visualize them in a grafana dashboard.
In particular the project aims to provide a solution for reading and monitoring OBD-II (On-Board Diagnostics) data from a vehicle, log the data in a local SQLite database, and periodically send it to a remote server. The system also uses LED indicators to provide feedback on the vehicle's connection status and operations. The software is designed to run as a systemd service on a Linux-based environment. 

### Key Features:
- OBD-II data collection and logging
- LED feedback system (Blue, Red, Green)
- SQLite database to store sensor data
- Remote server data upload via rsync
- Gear estimation from RPM and speed
- Automatic reconnection to OBD and Bluetooth
- Graceful shutdown using a physical switch
- Error logging and handling
- Data transmission only when connected to Wi-Fi
- Configurable sensor list and scanning interval

## Hardware Requirements:
- [OBD2 Scanner compatible with ELM327 Commands](https://www.amazon.it/dp/B071D8SYXN?ref=ppx_yo2ov_dt_b_fed_asin_title) - I suggest this scanner because is cheap enough but it's not a chinese copy of real ones.
- [Raspberry pi zero 2w](https://www.amazon.it/dp/B09KLVX4RT?ref=ppx_yo2ov_dt_b_fed_asin_title) - Cheapest raspberry with wifi and bluetooth that draws little power
- [microSD](https://www.amazon.it/SanDisk-microSDXC-adattatore-prestazioni-dellapp/dp/B0B7NXBM6P) - I reccomend an A1 card like this
- [DC converter from 12/24V to 5V 3A](https://www.amazon.it/dp/B0CHJN3J2Y?ref=ppx_yo2ov_dt_b_fed_asin_title) - To power up the raspberry directly from the car battery
- USB-A to micro-USB cable
- Switch/Button - A normal switch or button to power on or off the raspberry
- 3 leds - I recomment 3 different colors or 2 multicolor leds.
- other sensors (DHT11 for temperature, GPS, Accelerometer, etc). 


## Software Components

### 1. **Systemd Service: `car_scanner.service`**
The service is designed to run the main Python script (`main.py`) automatically as a background service on system startup. It ensures that the service restarts on failure.

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
git clone https://github.com/DavideSirico/car_scanner.git
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


## Check OBD-II Connection 
Step 1 - Try to connect to OBD Adapater via Bluetooth manually
```
bluetoothctl
help <-- see all the commands
show
power on
pairable on
agent on <-- used for persisting pairing code
default-agent
scan on <-- find OBDII and its MAC address
pair <mac_address> <-- enter pin 1234
trust <mac_address> <-- this will allow Pi to automatically pair with the device next time
scan off
quit
```
Step 2 - Connect Car with Screen
```
sudo rfcomm bind hci0 <mac_address>
screen /dev/rfcomm0
atz
atl1
ath1
atsp0 <-- use protocol auto, available protocols: 1, 2, 3, 4, 5, 6, 7, 8, 9, A
0100 <-- mode 01, pid 00, supported pids
```
If successfully connected to the car, 0100 will return something instead of "UNABLE TO CONNECT" or "CAN ERROR" or "BUS INIT: ...ERROR".

## Usage
Once installed and running, the system will automatically start collecting OBD-II data when the car is turned on. Data will be saved locally and transmitted to the remote server periodically. LEDs will provide status feedback:
- **Blue LED**: Indicates OBD-II connection status.
- **Green LED**: Blinks during data transmission.
- **Red LED**: Indicates system status (active when the system is running).

## Shutdown Procedure
A physical switch connected to a GPIO pin (specified in `config.json`) allows the system to gracefully shut down when released.

## To-Do List
- [ ] Improve LED intensity control
- [ ] Handle database errors more gracefully
- [ ] Refactor the gear estimation function into a class method

## Elettric circuit
For the energy to power up the raspberry I recommend to get it directly from the battery.
To make sure you don't set the car on fire I used a fuse on the positive sign. 
Next I connected the battery to the DC converter from 12/24V to 5V 3A. With this and a simple cable you can finally turn on the raspberry pi.
Connect the Raspberry to the leds and the switch.
The leds are connected to the GPIO pins of the raspberry pi.
The switch is connected to the GPIO pin and to the ground.
This project is still in progress, and contributions or suggestions are welcome.