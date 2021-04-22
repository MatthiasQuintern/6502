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

A = [27, 22, 10, 9, 11, 5, 6, 13,
     17, 4, 3, 2, 
     23, 18, 15] 

IO = gpio_r[4:12]  # 8 io pins
IO.reverse()

OEb = 26    # Output Enable
WEb = 19    # Write Enable
CEb = 14     # Chip Enable is hooked up to A15 on the processor

controls = [CEb, WEb, OEb]

# TIMES
# Read:
t_ACC = 150 * 1e-9  # Address to Output Delay

# Write:
t_AS = 0            # Address Setup time
t_AH = 50 * 1e-8    # Address Hold Time
t_CS = 0            # Chip Select Hold Time
t_WP = 100 * 1e-8   # Write Pulse Width
t_DS = 50 * 1e-8    # Data Setup Time_CS = 0
t_DH = 0            # Data Hold Time
t_WPH = 50 * 1e-8   # Write Puls High
# t_WPH = 50 * 1e-4   # Write Pulse High !!!2*e5 longer than in Datasheet, since shorter high caused Problems with my Chip!!!

# setup the pins
GPIO.setmode(GPIO.BCM)
for pin in controls:
    GPIO.setup(pin, OUT, initial=1)  # inverted, is 1 means disable

def setup_pins(IOdirection=OUT):
     # OUT when writing and IN when reading
    for pin in A:
        GPIO.setup(pin, OUT, initial=0)
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


def set_address(address: int, bits=8):
    """
    set the address pins to the gIOven value
    """
    ad_bin = format(address, f"0{bits}b")  # get the x-bit verion if the address, eg 12 -> 00001100
    for j in range(bits):
        # print("Address:", address, ad_bin, j)
        if ad_bin[bits-1-j] == "0":
            GPIO.output(A[j], 0)
        elif ad_bin[bits-1-j] == "1":
            GPIO.output(A[j], 1)
    return ad_bin


def get_bits(i: int):
    """
    return how many bits are needed to express the number in binary
    """
    return len(bin(i)) - 2  # -2 for the "0x"


def check_valid_list(l: list, bits=8):
    """
    check if the list only has x-bit binary numbers
    """
    for line in l:
        if not fullmatch("[01]{8}", line):
            return False
    return True

def get_8_bit(l: list):
    for i in range(len(l)):
        l[i] =  format(l[i], f"08b")  # get the 8-bit bin value
    return l

def erase(from_ad=0, to_ad=32767, **keys):
    """
    Write all 1 to the EEPROM
    WEb controlled
    """
    data = [0xff for i in range(from_ad, to_ad)]
    write(data, from_ad=from_ad, **keys)
    print("Erased EEPROM - Done!")
    return


def read(from_ad=0, to_ad=255, delay=1e-3, ignore=[0xff], verbose=True, single_step=False):
    """
    from_ad:    start address from where to read
    to_ad:      end address to read to
    delay:      delay between readings in s
    verbose     wether to print the reading
    ignore      list of values which are not printed
    """
    setup_pins(IN)
    GPIO.output(WEb, 1)

    content = []
    bits = get_bits(to_ad)

    for i in range(from_ad, to_ad + 1):
        # set the address valid
        ad_bin = set_address(i, bits=bits)

        # low in chip/output enable -> enable
        GPIO.output(CEb, 0)
        GPIO.output(OEb, 0)

        # wait the "Address to Output Delay" untol the output is valid
        sleep(t_ACC)

        byte = ""
        for j in range(8):
            # print(i, j, GPIO.input(IO[j]))
            if GPIO.input(IO[7-j]) == 1:
                byte += "1"
            else:
                byte += "0"
        
        # high in OEb and CEb -> disable
        GPIO.output(OEb, 1)
        GPIO.output(CEb, 1)
        
        content.append(byte)
        
        if verbose and not (int(byte, 2) in ignore):
            print(f"Reading:\t0b{format(int(ad_bin, 2), '015b')} - 0b{byte} ||| 0x{format(i, '04x')} - {hex(int(byte, 2))}")

        # wait artifical delay
        sleep(delay)
        
        if single_step:
            input("Press Return to read the next byte")

    GPIO.cleanup(IO)    
    GPIO.cleanup(A)
    sleep(1)
    return content


def write(content: list, from_ad=0, delay=0, single_step=False, verbose=True):
    """
    Write a list if bytes to the eeprom. 
    WEb controlled
    """
    content = get_8_bit(content)

    # how many bits are needed for the address
    ad_bits = get_bits(from_ad + len(content) - 1)
    # print(ad_bits, len(content)) 
    print(f"Writing to EEPROM: {len(content)} bytes from address {from_ad}.")

    setup_pins(IOdirection=OUT)

    # ChipEnable
    GPIO.output(CEb, 0)

    # Just to be sure, disable OutputEnable
    GPIO.output(OEb, 1)

    # wait "Chip Select Time"
    sleep(t_CS) 

    for i in range(len(content)):
        # setup the address
        ad_bin = set_address(from_ad + i, bits=ad_bits)
        
        # wait "Address" Setup Time
        sleep(t_AS)

        # Start the write pulse -> enable WEb
        GPIO.output(WEb, 0)
        
        # wait "Address Hold Time"
        sleep(t_AH)
        
        # the bit that is used to determine the end of the write cycle
        poll_bit = content[i][7]

        # Setup Data
        for j in range(8):
            if content[i][7-j] == "1":
                bit = 1
            else:
                bit = 0
            GPIO.output(IO[j], bit)
        
        # wait "Data Setup Time"
        sleep(t_DS)
        # wait until minimum write pulse width is reached. in theory, should be t_WP-t_DS but this caused problems
        sleep(t_WP)

        # End Write Pulse -> disable WEb
        GPIO.output(WEb, 1)
        
        # wait "Data Hold"
        sleep(t_DH)

        # poll the written data
        for pin in IO:
            GPIO.cleanup(pin)
            GPIO.setup(pin, GPIO.IN)
        GPIO.output(OEb, 0)
        while not GPIO.input(IO[7]) == int(poll_bit):
            pass
        GPIO.output(OEb, 1)
        for pin in IO:
            GPIO.cleanup(pin)
            GPIO.setup(pin, GPIO.OUT)


        # wait "Write Pulse High"
        sleep(t_WPH)

        sleep(delay)
        if verbose:
            print(f"Writing:\t0b{format(int(ad_bin, 2), '015b')} - 0b{content[i]} ||| 0x{format(from_ad+i, '04x')} - {hex(int(content[i], 2))}")

        if single_step:
            input("Press Return to write the next byte")
    
    # disable ChipEnable 
    GPIO.output(CEb, 1)

    GPIO.cleanup(IO)    
    GPIO.cleanup(A)
    sleep(1)
    print("Write to EEPROM - Done!")
    return
        
def write_file(filepath, **keys):
    with open(filepath, "rb") as file:
        bindata = []
        for byte in file.read(): 
            bindata.append(byte)
    write(bindata, **keys)

action = None
file = None
from_ad = 0
to_ad = 32767  #2^15 -1 
delay = 0
single_step = False
verbose = False
ignore = [0xff]
content = []

if len(argv) > 1:
    for i in range(1, len(argv)):
        arg = argv[i]
        if argv[i-1] == "-w":
            action = "write_file"
            file = arg
        elif argv[i-1] == "-wh":
            action = "write_hex"
            content = arg.split(",")
            for i in range(len(content)):
                content[i] = int(content[i].replace("0x", ""), 16)
        elif arg == "-r":
            action = "read"
            verbose=True
        elif arg == "-e":
            action = "erase"
        elif arg == "-h":
            action = "help"
        
        # Addresses
        elif argv[i-1] == "--from":
            if "0x" in arg:
                from_ad = int(arg.replace("0x", ""), 16)
            else:
                from_ad = int(arg)
        elif argv[i-1] == "--to":
            if "0x" in arg:
                to_ad = int(arg.replace("0x", ""), 16)
            else:
                to_ad = int(arg)
        # options
        elif argv[i-1] == "--delay":
            delay = float(arg)
        elif arg == "--single_step":
            single_step = True
        elif arg == "--verbose":
            verbose = True
        elif argv[i-1] == "--ignore":
            ignore = arg.split(",")
            for i in range(len(ignore)):
                ignore[i] = int(ignore[i].replace("0x", ""), 16)

# print(action, file, from_ad, to_ad)
if action == "write_file":
    write_file(file, from_ad=from_ad, delay=delay, single_step=single_step, verbose=verbose)
elif action == "write_hex":
    write(content, from_ad=from_ad, delay=delay, single_step=single_step, verbose=verbose)
elif action == "read":
    read(from_ad=from_ad, to_ad=to_ad, delay=delay, single_step=single_step, verbose=verbose, ignore=ignore)
elif action == "erase":
    erase(from_ad=from_ad, to_ad=to_ad, delay=delay, single_step=single_step, verbose=verbose)
elif action == "help":
    print("""
program options:
    -w  file        write file
    -e              erase eeprom
    -r              read eeprom
    -h              print this
    --from x        start at address x (can be int or hex with '0x' prefix))
    --to y          end at address y
    --single_step   single step the program
    --delay t       extra delay t between cycles
    --verbose       print extra information
    --ignore a,b,.. ignore the numbers a,b,... (in hex) when printing. Default is 0xff
if no option is given the GPIO-Pin-settings are printed
          """)
else:
    print("No valid action given. Printing Pin-Settings")
    print_pins()
# if performing action from this script, put the code HERE:


GPIO.cleanup()







