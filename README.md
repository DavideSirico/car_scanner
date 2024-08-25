
# Car Scanner
This project is made to collect, display and analyze information about your car.

## Requirements:
- [OBD2 Scanner compatible with ELM327 Commands](https://www.amazon.it/dp/B071D8SYXN?ref=ppx_yo2ov_dt_b_fed_asin_title) - I suggest this scanner because is cheap enough but it's not a chinese copy of the real one.
- [Raspberry pi zero 2w](https://www.amazon.it/dp/B09KLVX4RT?ref=ppx_yo2ov_dt_b_fed_asin_title) - Cheapest raspberry with wifi and bluetooth that draw little power
- [microSD]() - I reccomend an A1 card like this
- [DC converter from 12/24V to 5V 3A] - (https://www.amazon.it/dp/B0CHJN3J2Y?ref=ppx_yo2ov_dt_b_fed_asin_title)
- Switch/Button - A normal switch or button to power on or off the raspberry (u can configure if let always on or turn it on manually)
- 3 leds
- other sensors (DHT11 for temperature, GPS, Accelerometer)

## Elettric circuit


## Installation
Install raspbianOS lite on the microSD

### turn on the raspberry and connect through SSH
### update and install the required packages 
sudo apt update && sudo apt upgrade -y
sudo apt install bluetoothd bluez git python3 screen
### clone this repo
git clone https://github.com/DavideSirico/car_scanner
### create a python virtual enviroment
python3 -m venv .venv

### activate the python env
source .venv/bin/activate

### install the required package
python -m pip install -r requirements.txt

Step 1 - Connect OBD Adapater via Bluetooth
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

Check if the connection is working
Step 2 - Connect Car with Screen (Optional)
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



create a systemlink for the service 
sudo ln -s /home/david/car_scanner/car_scanner.service /etc/systemd/system/

change the variable in the sender.py and reader.py files

## program structure
3 scripts:
- The reader.py collects and save the data from the DHT11, GPS and from the OBD Scanner in an sqlite3 database. 
- The sender.py checks if the raspberry is connected to wifi and sends the data to the server that i have at home the database through ssh.
- The  ... is monitoring the switch to power on/off the raspberry.

3 services:
- TODO
- TODO
- TODO


## main features

