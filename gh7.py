#!/usr/bin/python
#encoding: utf-8

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
from time import sleep
import urllib3
from RPLCD import CharLCD

# THINKSPEAK ACCOUNT
tsKey = 'E55K9NU1FSMNEIA7'
tsUrl = 'https://api.thingspeak.com/update?api_key='


# Read temperature and humidity
def readDHT():
    H, T = Adafruit_DHT.read_retry(11, 18)
    if H is not None and T is not None:
        print('Temp: {0:0.1f}*C  Humid: {1:0.1f}%'.format(T, H))
        return (str(T), str(H))
    else:
        print('Did not get a reading')

# Diplay temperature and humidity on screen


def display():
    lcd = CharLCD(cols=16, rows=2, pin_rs=5, pin_e=6, pins_data=[13, 19, 26, 16])
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp: %d C" % T)
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Humid: %d %%" % H)
    

# Main function
def main():

    global tsKey
    global tsUrl

    while True:
      try:
        readDHT()
        display()
        conn = urllib3.urlopen(tsUrl + tsKey + "&field1=%s&field2=%s" % (T, H))
        print(conn.read())
        conn.close()
        sleep(12)

      except:
        break

if __name__ == '__main__':
    main()
    
