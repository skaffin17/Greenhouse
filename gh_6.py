#!/usr/bin/env python
#encoding: utf-8

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
from time import sleep
import urllib3

# THINKSPEAK ACCOUNT
tsKey = 'E55K9NU1FSMNEIA7'
tsUrl = 'https://api.thingspeak.com/update'


# Read temperature and pressure
def readDHT():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 27)
    # return dict
    print(str(RH), str(T))
    return (str(RH), str(T))
    

# Main function
def main():

    global tsKey
    global tsUrl

    while True:
      try:
        RH, T = readDHT()
        f = urllib3.urlopen(tsUrl + tsKey + "&field1=%s&field2=%s" % (RH,T))
        print(f.read())
        f.close()
        sleep(120)

      except:
        print('exiting...')
        break

if __name__ == '__main__':
    main()
    
