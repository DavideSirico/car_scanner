
# Car Scanner
This project is made to collect, display and analyze information about your car and visualize them in a grafana dashboard. 

## Requirements:
- [OBD2 Scanner compatible with ELM327 Commands](https://www.amazon.it/dp/B071D8SYXN?ref=ppx_yo2ov_dt_b_fed_asin_title) - I suggest this scanner because is cheap enough but it's not a chinese copy of the real one.
- [Raspberry pi zero 2w](https://www.amazon.it/dp/B09KLVX4RT?ref=ppx_yo2ov_dt_b_fed_asin_title) - Cheapest raspberry with wifi and bluetooth that draws little power
- [microSD]() - I reccomend an A1 card like this
- [DC converter from 12/24V to 5V 3A] - (https://www.amazon.it/dp/B0CHJN3J2Y?ref=ppx_yo2ov_dt_b_fed_asin_title)
- USB-A to micro-USB
- Switch/Button - A normal switch or button to power on or off the raspberry
- 3 leds - I recomment 3 different colors or 2 multicolor leds.
- other sensors (DHT11 for temperature, GPS, Accelerometer)

## Elettric circuit
For the energy to power up the raspberry I recommend to get it directly from the battery like this:
TODO PHOTO
To make sure you don't set the car on fire I used a fuse on the positive sign. 
Next I connected the battery to the DC converter from 12/24V to 5V 3A. With this and a simple cable you can finally turn on the raspberry pi.

Connect the Raspberry to the leds and the switch.
(TODO PHOTO)


## Installation
### update and install the required packages 

```bash
$ sudo apt update && sudo apt upgrade -y
```
```bash
$ sudo apt install bluetoothd bluez git python3 screen
```

### clone this repo
`git clone https://github.com/DavideSirico/car_scanner`
### create a python virtual enviroment
```python3 -m venv .venv```
### activate the python env
```source .venv/bin/activate```
### install the required package
```python -m pip install -r requirements.txt```

## Usage 
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

Check if the connection is working
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

### change the variable in the sender.py and reader.py files

### make the 2 scripts running at startup
create a systemlink for the service 
```
sudo ln -s /home/david/car_scanner/car_scanner.service /etc/systemd/system/
```

## program structure


## main features
- Saving car sensors' data in a database (SQLite3)
- Sending data to another server when the car is at home
- Auto connection to the OBD Scanner
- Logging for finding errors




## TODO:
 - temperature and humidity sensor
 - multicolor led
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTE2MDkxMDA4NDYsNzg2OTYwOTUzLDE4Nj
I3MDQ2NzUsLTE3NTUzMjAwNjBdfQ==
-->