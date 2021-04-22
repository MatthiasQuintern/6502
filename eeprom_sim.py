from sys import argv
from time import sleep
from RPi.GPIO import IN, OUT
import RPi.GPIO as GPIO
from re import fullmatch
# EEPROM AT28C256 Pin names and RPi GPIO Pin Numbers
# b means bar = inverted


gpio_l = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26]
gpio_r = [14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
#
# Defining which 6502 pin goes to which GPIO pin
#

IO = gpio_r[-8:]  # 8 io pins
IO.reverse()
A = [13, 6, 5, 11, 9, 10, 22, 27,
     17, 4, 3, 2, 
     23, 18, 15] 

OEb = 26    # Output Enable
WEb = 19    # Write Enable
CEb = 14     # Chip Enable is hooked up to A15 on the processor
controls = [CEb, WEb, OEb]

# setup the pins
GPIO.setmode(GPIO.BCM)
for pin in controls:
    GPIO.setup(pin, IN)
for pin in A:
    GPIO.setup(pin, IN)

def setup_pins(IOdirection=OUT):
     # OUT when writing and IN when reading
    for pin in IO:
        if IOdirection == OUT:
            GPIO.setup(pin, IOdirection, initial=0)
        elif IOdirection == IN:
            GPIO.setup(pin, IOdirection)


def print_pins():
    for i in range(len(A)):
        print(f"A{i} - {A[i]}")
    for i in range(len(IO)):
        print(f"IO{i} - {IO[i]}")
    print(f"CEb - {CEb}")
    print(f"WEb - {WEb}")
    print(f"OEb - {OEb}")

def get_8_bit(l: list):
    for i in range(len(l)):
        l[i] =  format(l[i], f"08b")  # get the 8-bit bin value
    return l

def simulate(path, verbose=True):
    with open(path, "rb") as file:
        bindata = file.read()
    data = []
    for i in range(len(bindata)):
        data.append(format(bindata[i], "08b"))
    address_old = -1
    while True:
        # assumes the EEPROM is only hooked up via CE. If CE is low, it will ouput data
        if not  GPIO.input(CEb) == 0:
            GPIO.cleanup(IO)
            continue
        # decode the address
        ad_s = ""
        for i in range(len(A)):
            ad_s += str(GPIO.input(A[len(A)-1-i]))
        address = int(ad_s, 2)
        
        if address != address_old:
            # put the data on the bus
            setup_pins(OUT)
            for i in range(8):
                if data[address][i] == "0":
                    GPIO.output(IO[7-i], 0)
                else:
                    GPIO.output(IO[7-i], 1)
            # wait the output hold time
            if verbose:
                print(f"{bin(address)} - {data[address]}|||{hex(address)} - {hex(int(data[address], 2))}")
            address_old = address







if len(argv) > 1:
    simulate(argv[1])
else:
    print("No filepath given. Printing Pin-Settings")
    print_pins()
# if performing action from this script, put the code HERE:


GPIO.cleanup()







