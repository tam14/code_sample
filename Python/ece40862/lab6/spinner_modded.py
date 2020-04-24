from machine import I2C, Pin, PWM, Timer
from math import sqrt, pow, atan
import time
import ustruct

window_length = 50

temp_mask = 0x7fff
accel_mask = 0x01ff

average_x = 0
average_y = 0
average_z = 0

prev_temp = 0
curr_temp = 0
comp_temp = 0

button = 0

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def update_average(window, new_val) -> int:
    window[1 : window_length] = window[0 : window_length-1]
    window[0] = new_val
    return sum(window) / window_length

def interface_sensors():
    global led_g
    global led_r
    global led_y
    
    led_g.value(1)
    led_r.value(1)
    led_y.value(1)
    
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
        
        global prev_temp
        temp_raw = int.from_bytes(i2c.readfrom_mem(0x48, 0x00, 2), 'big')
        temp_mag = (temp_raw & 0x7fff)
        temp_sig = (temp_raw & 0x8000) >> 7
        prev_temp = (1 - 2 * temp_sig) * temp_mag * .0078
        
def button_press(pin) :
    global button
    
    if pin == Pin(14) and button != 1 :
        button = 1
    elif pin == Pin(15) and button == 1 :
        button = 2
    
    button_timer.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed)

# main code
i2c = I2C(1, scl=Pin(22), sda=Pin(23), freq=400000)
    
button_g = Pin(14, Pin.IN, Pin.PULL_UP)
button_g.irq(trigger=Pin.IRQ_FALLING, handler=button_press)
button_r = Pin(15, Pin.IN, Pin.PULL_UP)
button_r.irq(trigger=Pin.IRQ_FALLING, handler=button_press)
button_timer = Timer(1)

onboard = PWM(Pin(13))
onboard.freq(0)
onboard.duty(0)

l = 1
m = 1
while (True):   
    if button > 0 :
        curr_temp = i2c.readfrom_mem(0x48, 0x00, 2)
        accel_val_x = i2c.readfrom_mem(0x53, 0x32, 2)
        accel_val_y = i2c.readfrom_mem(0x53, 0x34, 2)
        accel_val_z = i2c.readfrom_mem(0x53, 0x36, 2)
        
        if button > 1 :
            
    time.sleep_ms(1)

