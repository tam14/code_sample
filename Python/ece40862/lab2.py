import machine
from machine import Timer, ADC, Pin, PWM
import time
import sys
import micropython

# some global vars to hold state and to keep track of how long it's been since the last red-led frequency change
state = 0
ignore = 0

# gpio peripheral initialization
button = Pin(14, Pin.IN, Pin.PULL_UP)
red_led = Pin(17, Pin.OUT, value=1)

# function that prints the date and time. called every 30 seconds
def print_datetime(_) :
    year, month, day, _, hour, minute, second, _ = rtc1.datetime()
    print("{}/{}/{}, {}:{}:{}".format(month, day, year, hour, minute, second))

# function that reads the potentiometer value
def read_adc(_) :
    global adc1
    global state
    global led_timer
    global ignore
    
    adc_val = adc1.read() + 1
        
    if state == 1 :
        if ignore >= 5 :
            ignore = 0
            led_timer.deinit()
            led_timer = Timer(3)
            led_timer.init(mode=Timer.PERIODIC, period=int(4096*15/adc_val), callback=red_pin)
        else :
            ignore = ignore + 1
    elif state == 2 :
        pwm16.duty(int(adc_val/4))

# change the red led from off to on and vice versa
def red_pin(_) :
    global red_led
    red_led.value(not red_led.value())

# if acknowledged that the button was pressed, set the state
def on_pressed(_) :
    global state
    
    if state == 0 :
        state = 1
    elif state == 1 :
        state = 2
    elif state == 2 :
        state = 1
    else :
        state = 1

# if button is pressed, starts a timer that waits 200ms before acknowledging that it was pressed
def button_press(_) :
    buttom_timer.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed)
    
# initialize the real time clock
rtc1 = machine.RTC()
rtc1.init((int(input("Year? ")), int(input("Month? ")), int(input("Day? ")), int(input("Weekday? ")), int(input("Hour? ")), int(input("Minute? ")), int(input("Second? ")), int(input("Microsecond? "))))

# call a function that prints the date and time every 30 seconds
rtc_timer = Timer(0)
rtc_timer.init(mode=Timer.PERIODIC, period=30000, callback=print_datetime)

# initialize the adc port
adc1 = ADC(Pin(32))
adc1.atten(ADC.ATTN_11DB)
adc1.width(ADC.WIDTH_12BIT)

# call a funciton that checks the potentiometer reading @10Hz
adc_timer = Timer(2)
adc_timer.init(mode=Timer.PERIODIC, period=100, callback=read_adc)

# start the green led blinking
pwm16 = PWM(Pin(16))
pwm16.freq(10)
pwm16.duty(256)

pwm17 = PWM(Pin(17))
pwm16.freq(10)
pwm16.duty(256)

# attach button debouncer thing
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press)
buttom_timer = Timer(1)

# start a timer that control the red led
led_timer = Timer(3)
led_timer.init(mode=Timer.PERIODIC, period=50, callback=red_pin)
