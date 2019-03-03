#!/usr/bin/python
#encoding: utf-8

import sys
import RPi.GPIO as GPIO
import thingspeak
import datetime
import Adafruit_DHT
from time import sleep
import urllib
from RPLCD import CharLCD

global chId = 673945                                   # Thingspeak Channel Id
global tsKey='NAK14Z0XFYQHBRGA'                        # Thingspeak API key
global tsUrl='https://api.thingspeak.com/update?'      # Thingspeak data update url
global ts = thingspeak.Channel(tsUrl ,tsKey, chId)

# Read temperature and humidity
def readDHT():
    humi, temp = Adafruit_DHT.read_retry(11, 18)
    if humi is not None and temp is not None:
        print('Temp: {0:0.1f}*C  Humidity: {1:0.1f}%'.format(temp, humi))
        return (str(temp), str(humi))
    else:
        print('Did not get a reading')

# Diplay temperature and humidity on screen
def display():
    lcd = CharLCD(cols=16, rows=2, pin_rs=5, pin_e=6, pins_data=[13, 19, 26, 16])
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp: %d C" % temp)
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Humidity: %d %%" % humi)
    

# Main function
def main():

    while True:
      try:
        readDHT()
        display()
        data = {
            "field1":temp,
            "field2":humi
            }
        ts.update(data)
        print ("Data sent")
        sleep(60)

      except:
        print("Error sending data")

if __name__ == '__main__':
    main()
    
