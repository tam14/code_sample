import time
from umqtt.robust import MQTTClient
from random import randint
import ubinascii
import machine
import micropython
import network
import utime
import ntptime
import esp32
from crypt import *
from machine import I2C, Pin, PWM, Timer
import ustruct
import utime

hard_timer1 = machine.Timer(0) #hardware

# LED
led_r = Pin(12, Pin.OUT, value=0)
pwm_g = machine.PWM(Pin(27), freq=500, duty=512)

# hotspot values
network_name = 'lenovo_half_laptop'
network_password = 'bigdoodle'

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(network_name, network_password)
        while not wlan.isconnected():
            pass
    print('Oh Yes! Get connected')
    print('Connected to Network')
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
    print('MAC Address: ', mac)
    print('IP Address: ', wlan.ifconfig()[0])
    

client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = 'farmer.cloudmqtt.com'
username = 'egenfaqd'
password = 'i0q7Q84p2Ueq'
port = 14219

prev_temp = 0

json_message = bytes()
mail_flag = 0 # you've got mail
    
def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def sub_cb(topic, msg):
    print("Received data from topic {}".format(topic))
    global json_message, mail_flag
    if topic == b'Sensor_Data':
        json_message = msg
        mail_flag = 1


def hard_handleInterrupt1(hard_timer1):
    try:
        ca.regen()
        client.publish(b'SessionID', ca.sessionID)

    except OSError as e:
        restart_and_reconnect()
   
# Main Function
do_connect()
ca = CryptAes()

client = MQTTClient(client_id=client_id, server=mqtt_server, port=port, user=username, password=password)
client.set_callback(sub_cb)
client.connect()
client.subscribe(b'Sensor_Data')
print("Connected to MQTT Broker")

#hard_timer1.init(period=1000, mode=machine.Timer.PERIODIC, callback=hard_handleInterrupt1)
client.publish(b'SessionID', ca.sessionID)
print("published message")
ticks_1 = utime.ticks_ms()

while True:
    new_message = client.check_msg()
    time.sleep_us(1000)
    if mail_flag == 1:
        mail_flag = 0
        result = ca.verify_hmac(json_message)
        ticks_2 = utime.ticks_ms()
        print(utime.ticks_diff(ticks_2, ticks_1))
        
        if result:
            client.publish(b'Acknowledge', b'Successful Decryption')
            print("Authentication Passed. Decrypting")
            (d_iv, d_nodeid, d_data) = ca.decrypt()
            print("Successful Decryption")
            accel_val_x = ustruct.unpack("<h", d_data[0:2])[0]
            accel_val_y = ustruct.unpack("<h", d_data[2:4])[0]
            accel_val_z = ustruct.unpack("<h", d_data[4:6])[0]
            if abs(accel_val_x) > 1 or abs(accel_val_y) > 1 or abs(accel_val_z) > 1:
                led_r.value(1)
            else:
                led_r.value(0)

            curr_temp = twos_comp(int.from_bytes(d_data[6:8], 'big'), 16) * .0078
            if curr_temp > (prev_temp + 1):
                pwm_g.freq(pwm_g.freq() + 5)
            
        else:
            client.publish(b'Acknowledge', b'Failed Authentication')
            print("Authentication Failed")