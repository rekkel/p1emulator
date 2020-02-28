# P1 Emulator

The P1 Emulator is a python based application which turns your Raspberry Pi Touchscreen into a SMR5 smart meter P1 port. The application lets the user generate telegram messages on the P1 port.
This can be done by fixed voltage and current values per phase. Or by random generated voltage and current values per phase, based on minimum and maximum values. In all cases the power per phase, import, export and tariffs will be calculated automatically.

## Installation

Most Linux OS's have python3 installed by default. If not, install it. 
Make sure the following files are in the same directory: P1emulator.py, dsmr_emulator.py and smartmetericon.png
They all should be readable and the python files should be executable for all user levels.

Make sure the desktop icon is at the desired desktop to start the application: ~/Desktop/P1Emulator.desktop

On your Linux system, open: File manager --> Edit --> Preferences --> General  
- Check: Open files with single click
- Check: Do not ask option on executable launch

Now the program can be successfully started by ticking the desktop icon.

## Mandatory hardware

The application outputs the serial data on /dev/ttyUSB0. Connect a FTDI TTL-232R-5V cable to the USB port of your Raspberry Pi.  
Download the FTDI program application FT_PROG to invert TXD on the FTDI TTL-232R-5V. 

An alternative to the FTDI cable requirements above is to configure the Raspberry Pi's GPIO pins for serial inverted output.



# p1emulator
