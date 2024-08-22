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

Step 2 - Connect Car with Screen (Optional)
```
screen /dev/rfcomm0
atz
atl1
ath1
atsp0 <-- use protocol auto, available protocols: 1, 2, 3, 4, 5, 6, 7, 8, 9, A
0100 <-- mode 01, pid 00, supported pids
```
If successfully connected to the car, 0100 will return something instead of "UNABLE TO CONNECT" or "CAN ERROR" or "BUS INIT: ...ERROR".

Step 3 - Connect Car with Python OBD
* Create a serial port: ```sudo rfcomm bind hci0 <mac_address>```


create a python virtual enviroment
python3 -m venv .venv

activate the python env
source .venv/bin/activate

install the required python package
pip install -r requirements.txt

create a systemlink for the service 
sudo ln -s /home/david/car_scanner.service /etc/systemd/system/

change the variable in the sender.py and reader.py files