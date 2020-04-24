import time
from umqtt.robust import MQTTClient
import ubinascii
import machine
import micropython
import network
import utime
import ntptime
import esp32


# hotspot values
network_name = 'lenovo_half_laptop'
network_password = 'bigdoodle'

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

client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = 'farmer.cloudmqtt.com'
port = 14219
username = 'egenfaqd'
password = 'i0q7Q84p2Ueq'

def sub_cb(topic, msg):
    print((topic, msg))

topic_session = b'SessionID'
topic_data = b'Sensor_Data'
topic_ack = b'Acknowledge'

connect_to_internet()

c = MQTTClient(client_id=client_id, server=mqtt_server, port=port, user=username, password=password)
c.set_callback(sub_cb)
c.connect()
c.subscribe(topic_sub)

while True:
    new_message = c.check_msg()
    if new_message != 'None':
        c.publish(topic_pub, b'received')
    time.sleep(1)
c.disconnect()
