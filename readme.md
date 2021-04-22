# 8-bit Breadboard Computer with W65C02S Processor
This repo contains python and assembly programs for my 6502-project.

## EEPROM Utility (with Raspberry Pi 4)
"eeprom.py" is a python program for reading and writing to an EEPROM. It should work for the AT28C256 but might also work for other (you will eventually have to adjust the hold/setup-times).
To print the options, use
    python3 eeprom.py -h

"eeprom_sim.py" is a pyhton script which emulates the AT28C256 EEPROM. This is useful when testing/debugging code, since you don't need to rewrite and replug the EEPROM after every change of the code. Instead, the Raspberry Pi is connected to the address- and databus, and the write-, read- and chip-enable. Then start the simulation with
    python3 eeprom_sim.py your_binary.bin 

## Debug-Utility (with Raspberry Pi 4)
"monitor.py" is a python program to monitor the address-bus, data-bus and the Read-Write Pin of the computer. It prints the current address and data in binary and hexadecimal on each clock cycle.

