import RPi.GPIO as GPIO
from RPi.GPIO import IN

# Monitor the 6502 processor
gpio_l = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26]
gpio_r = [14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
#
# Defining which 6502 pin goes to which GPIO pin
#

A = gpio_l[0:12]
A.reverse()         # first 11 address pins, left side of 6502
A += [23, 18, 15, 14]    # last 4 address pins

D = gpio_r[-8:]  # 8 io pins
D.reverse()

PHI2 = 26
RWB = 19

GPIO.setmode(GPIO.BCM)

# OUT when writing and IN when reading
for pin in [PHI2, RWB]:
    GPIO.setup(pin, IN)

for pin in A:
    GPIO.setup(pin, IN)

for pin in D:
    GPIO.setup(pin, IN)

def print_pins():
    for i in range(len(A)):
        print(f"A{i} - {A[i]}")
    for i in range(len(D)):
        print(f"D{i} - {D[i]}")
    print(f"PHI2 - {PHI2}")
    print(f"RWB - {RWB}")

def start_monitor():
    run = True
    while run:
        # wait for a rising clock edge before outputting
        channel = GPIO.wait_for_edge(PHI2, GPIO.FALLING, timeout=1000)    # at least every 1 seconds
        if channel is None:
            continue
        address = ""
        data = ""
        for i in range(len(A)):
            address += str(GPIO.input(A[len(A)-1-i]))
        for i in range(len(D)):
            data += str(GPIO.input(D[len(D)-1-i]))
        if GPIO.input(RWB):
            rwb = "r"
        else:
            rwb = "w"
        line = f"0b{address} - 0b{data}|||0x{format(int(address, 2), '04x')} - 0x{format(int(data, 2), '02x')}|||{rwb} "
        print(line)


print_pins()
try:
    start_monitor()
except KeyboardInterrupt:
    GPIO.cleanup()





