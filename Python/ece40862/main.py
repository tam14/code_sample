import machine
from machine import Timer, TouchPad, Pin
import network
import utime
import ntptime
import esp32

# hotspot values
network_name = 'lenovo_half_laptop'
network_password = 'bigdoodle'

def figure_out_reset_reason(wake_reason) :
    # print the reason for waking up after waking up 
    if wake_reason == 3 :
        print('Woke up due to Button')
    elif wake_reason == 4 :
        print('Woke up due to Sleep Timeout')
    elif wake_reason == 5 :
        print('Woke up due to Touchpad')
    else :
        pass

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

def print_datetime(_) :
    # prints the date and time as determined by the real time clock
    year, month, day, _, hour, minute, second, _ = rtc.datetime()
    print("Date: {:02d}/{:02d}/{:04d}\nTime: {:02d}:{:02d}:{:02d} HRS".format(month, day, year, hour, minute, second))
    
def measure_brown_touch(_) :
    # lights up led if brown wire is pressed
    val = touch33.read()
    if val < 325 :
        green_led.value(1)
    else :
        green_led.value(0)

def go_to_sleep(_) :
    # puts the board in deepsleep after 30seconds for 1minute
    print('I am awake. Going to sleep for 1 minute')
    red_led.value(0)
    machine.deepsleep(60000)

#initial setup functions
figure_out_reset_reason(machine.wake_reason())
connect_to_internet()

#get time tuple
tt = utime.localtime(ntptime.time()-4*60*60)
tm = (tt[0], tt[1], tt[2], tt[6], tt[3], tt[4], tt[5], 0)

# initialize the real time clock
rtc = machine.RTC()
rtc.init(tm)

# call a function that prints the date and time every 15 seconds
rtc_timer = Timer(0)
rtc_timer.init(mode=Timer.PERIODIC, period=15000, callback=print_datetime)

# initialize capacitive touch wires
touch27 = TouchPad(Pin(27))
touch27.config(325)
touch33 = TouchPad(Pin(33))

# initialize leds
green_led = Pin(16, Pin.OUT, value=1)
red_led = Pin(17, Pin.OUT, value=1)

# measure the value of one of the wires every 10 ms
touch_timer = Timer(1)
touch_timer.init(mode=Timer.PERIODIC, period=10, callback=measure_brown_touch)

# initialize a timer to put our board to sleep every 30s
sleep_timer = Timer(2)
sleep_timer.init(mode=Timer.PERIODIC, period=30000, callback=go_to_sleep)

# initialize_buttons
green_button = Pin(14, Pin.IN, Pin.PULL_DOWN)
red_button = Pin(15, Pin.IN, Pin.PULL_DOWN)

# set what can wake up the board
esp32.wake_on_touch(True)
esp32.wake_on_ext1(pins=[green_button, red_button], level=esp32.WAKEUP_ANY_HIGH)