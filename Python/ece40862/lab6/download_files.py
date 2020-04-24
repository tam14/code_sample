import machine
from machine import Timer, TouchPad, Pin
import network
import utime
import ntptime
import esp32

# hotspot values
network_name = 'tam14_t440s'
network_password = 'tam14_t440s'

def connect_to_internet() :
    # connect to wlan
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    if not nic.isconnected():
        # if it's not connected, wait until it is
        nic.connect(network_name, network_password)
        while not nic.isconnected():
            utime.sleep(1)
    
    # print out connection information
    print('Oh Yes! Get connected')
    print('Connected to {}'.format(nic.config('essid')))
    mac_string = ':'.join(hex(b).replace("0x", "") for b in nic.config('mac'))
    print('MAC Address: {}'.format(mac_string))
    print('IP Address: {}'.format(nic.ifconfig()[0]))
    
#initial setup functions
connect_to_internet()
