import time
from umqtt.robust import MQTTClient
import ubinascii
import machine
from machine import I2C, Pin, Timer, PWM
import micropython
import network
import utime
import ntptime
import os
import ustruct
from crypt import *

# hotspot values
network_name = 'tam14-xz1comp'
network_password = 'tam14connect'

# mqtt values
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = 'farmer.cloudmqtt.com'
port = 14219
username = 'egenfaqd'
password = 'i0q7Q84p2Ueq'

# topic names
topic_session = b'SessionID'
topic_data = b'Sensor_Data'
topic_ack = b'Acknowledge'

# sensor stuff
window_length = 50
temp_mask = 0x7fff
accel_mask = 0x01ff
button = 0

# session
sessionID = bytearray(16)
send_message = 0

def sub_cb(topic, msg):
    if topic == topic_session :
        global sessionID, send_message
        sessionID = msg
        send_message = 1
    elif topic == topic_ack :
        if msg == b'Successful Decryption':
            print("Target received good packet")
        else : 
            print("Target received bad packet")
        
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

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def update_average(window, new_val) -> int:
    window[1 : window_length] = window[0 : window_length-1]
    window[0] = new_val
    return sum(window) / window_length

def interface_sensors():
    # address 83 = 0x
    i2c.writeto_mem(0x53, 0x31, b'\x00')
    i2c.writeto_mem(0x53, 0x2c, b'\x0d')
    print("Set accelerometer output rate")
    i2c.writeto_mem(0x53, 0x2d, b'\x08')
    print("Enabled accelerometer measurements")
    
    # address 72 = 0x48 : temp sensor
    i2c.writeto_mem(0x48, 0x03, b'\x80')
    print("Configured temperature sensor resolution")
    
    # calibrate accelerometer
    x_list = [0] * 5
    y_list = [0] * 10
    z_list = [0] * 10
    x_error = 100
    y_error = 100
    z_error = 100
    
    # calibrate x axis
    print("Calibrating x-axis")
    while abs(x_error) > 2 :
        for i in range(0, 5) :
            x_list[i] = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x32, 2))[0]
        x_avg = sum(x_list) / 5
        
        # write offset to registers
        i2c.writeto_mem(0x53, 0x1e, bytearray([-round(x_avg/8)]))
        time.sleep_ms(10)
        
        for i in range(0, 5) :
            x_list[i] = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x32, 2))[0]
        x_error = sum(x_list) / 5
    
    
    # calibrate y axis
    print("Calibrating y-axis")
    while abs(y_error) > 2 :
        for i in range(0, 10) :
            y_list[i] = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x34, 2))[0]
        y_avg = sum(y_list) / 10
        
        # write offset to registers
        i2c.writeto_mem(0x53, 0x1f, bytearray([-round(y_avg/8)]))
        time.sleep_ms(10)
        
        for i in range(0, 10) :
            y_list[i] = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x34, 2))[0]
        y_error = sum(y_list) / 10    

    # calibrate z axis
    print("Calibrating z-axis")
    while abs(z_error) > 2 :
        for i in range(0, 10) :
            z_list[i] = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x36, 2))[0]
        z_avg = sum(z_list) / 10 - 256.4
        
        # write offset to registers
        curr_offset = twos_comp(int.from_bytes(i2c.readfrom_mem(0x53, 0x20, 1), 'big'), 8)
        curr_offset = curr_offset - round(z_avg/8)
        time.sleep_ms(10)
        i2c.writeto_mem(0x53, 0x20, bytearray([curr_offset]))
        time.sleep_ms(10)
        
        for i in range(0, 10) :
            z_list[i] = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x36, 2))[0]
        z_error = (sum(z_list) / 10) - 256.4        
        
    print("Accelerometer Calibration Complete")

def on_pressed(pin) :
    global button
    global onboard
    
    if button == 1 :
        onboard.freq(100)
        onboard.duty(512)
        interface_sensors()
    elif button == 2 :
        onboard.freq(10)
        onboard.duty(512)
        
def button_press(pin) :
    global button
    
    if pin == Pin(14) and button != 1 :
        button = 1
    elif pin == Pin(15) and button == 1 :
        button = 2
    
    button_timer.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed)

connect_to_internet()

# connect to mqtt broker
c = MQTTClient(client_id=client_id, server=mqtt_server, port=port, user=username, password=password)
c.set_callback(sub_cb)
c.connect()
c.subscribe(topic_session)
c.subscribe(topic_ack)

# initialize i2c
i2c = I2C(1, scl=Pin(22), sda=Pin(23), freq=400000)
    
# initialize buttons
button_g = Pin(14, Pin.IN, Pin.PULL_UP)
button_g.irq(trigger=Pin.IRQ_FALLING, handler=button_press)
button_r = Pin(15, Pin.IN, Pin.PULL_UP)
button_r.irq(trigger=Pin.IRQ_FALLING, handler=button_press)
button_timer = Timer(1)

onboard = PWM(Pin(13))
onboard.freq(0)
onboard.duty(0)

encrypter = CryptAes()

while True:
    new_message = c.check_msg()
    
    if button > 1 and send_message == 1:
        # read from sensors
        raw_t = i2c.readfrom_mem(0x48, 0x00, 2)
        raw_x = i2c.readfrom_mem(0x53, 0x32, 2)
        raw_y = i2c.readfrom_mem(0x53, 0x34, 2)
        raw_z = i2c.readfrom_mem(0x53, 0x36, 2)
        #temperature = twos_comp(int.from_bytes(raw_t, 'big'), 16) * .0078
        #accel_val_x = ustruct.unpack("<h", raw_x)[0] * .0039
        #accel_val_y = ustruct.unpack("<h", raw_y)[0] * .0039
        #accel_val_z = ustruct.unpack("<h", raw_z)[0] * .0039
        
        # package sensor data
        sensor_data = raw_t + raw_x + raw_y + raw_z
        
        # encryption stuff
        encrypter.regen_iv()
        encrypter.encrypt(sensor_data)
        given_hmac = encrypter.sign_hmac(sessionID)
        outbound_message = encrypter.send_mqtt(given_hmac)
        # publish message
        c.publish(topic_data, outbound_message)
        
        # clear flag
        send_message = 0
            
    time.sleep_ms(1)
