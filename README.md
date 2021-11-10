# 8-bit Breadboard Computer with W65C02S Processor
This repo contains python and assembly code for my 6502-project.

## Python Utilities (for usage with Raspberry Pi 4)
Here are some utilities I used to program and debug my 6502-Computer.
The fastest clock speed I ran them with was about 500Hz, but they might work with higher frequencies too (but certainly not with 1Mhz).

### EEPROM Reader/Writer
"eeprom.py" is a python program for reading and writing to an EEPROM. It should work for the AT28C256 but might also work for other (you will eventually have to adjust the hold/setup-times).
To print the options, use
    python3 eeprom.py -h

### EEPROM Simulator
"eeprom_sim.py" is a pyhton script which emulates the AT28C256 EEPROM. This is useful when testing/debugging code, since you don't need to rewrite and replug the EEPROM after every change of the code. Instead, the Raspberry Pi is connected to the address- and databus, and the write-, read- and chip-enable. Then start the simulation with
    python3 eeprom_sim.py your_binary.bin 

### Debug-Utility (with Raspberry Pi 4)
"monitor.py" is a python program to monitor the address-bus, data-bus and the Read-Write Pin of the computer. It prints the current address and data in binary and hexadecimal on each clock cycle.

## Operating System
... is probably a far stretch, since it is just the programs I wrote peaced together. My "os" consists of these functionalities:
- Main Menu:
    - Printer: Prints the characters you press on the keypad to the lcd.
    - Temperature: Shows the temperature using a dht sensor. *Work in progress, this does not work yet*
    - Text 1: Show a 4x16 character text (defined at compile time)
    - Text 2: Show a 4x16 character text (defined at compile time)
- Ringbuffer for pressed keys.

> It's not much, but it's honest work.

I compile the programs with **vasm** and load them on the eeprom using my *eeprom.py* script and the RPI's GPIO pins. 
