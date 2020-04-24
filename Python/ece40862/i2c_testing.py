from machine import I2C, Pin
import time
import ustruct

temp_mask = 0x7fff
accel_mask = 0x01ff

i2c = I2C(1, scl=Pin(22), sda=Pin(23), freq=400000)
print(i2c.scan())

# address 72 = 0x48 : temp sensor
i2c.writeto_mem(0x48, 0x03, b'\x80')

# address 83 = 0x53 : accelerometer
i2c.writeto_mem(0x53, 0x31, b'\x00')
i2c.writeto_mem(0x53, 0x2c, b'\x0d')
i2c.writeto_mem(0x53, 0x2d, b'\x08')

while (True):
    temp_raw = int.from_bytes(i2c.readfrom_mem(0x48, 0x01, 2), 'big')
    temp_val = temp_raw & temp_mask
    temp_sig = temp_raw >> 15
    #print((1 - 2 * temp_sig) * temp_val * .0078)
    
    accel_val_x = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x32, 2))[0]
    accel_val_y = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x34, 2))[0]
    accel_val_z = ustruct.unpack("<h", i2c.readfrom_mem(0x53, 0x36, 2))[0]
    print("({:+>05.2f}, {:+>05.2f}, {:+>05.2f})".format(accel_val_x * .0039, accel_val_y * .0039, accel_val_z *.0039))
    
    time.sleep_ms(50)