#!/usr/bin/env python
#encoding: utf-8

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
from time import sleep
import urllib3

# THINKSPEAK ACCOUNT
tsKey = 'E55K9NU1FSMNEIA7'
tsUrl = 'https://api.thingspeak.com/update?api_key='


# Read temperature and pressure
def readDHT():
    RH, T = Adafruit_DHT.read_retry(11, 18)
    if RH is not None and T is not None:
        print('Temp: {0:0.1f}*C  Humid: {1:0.1f}%'.format(T, RH))
        return (str(T), str(RH))
    else:
        print('Did not get a reading')

# Main function
def main():

    global tsKey
    global tsUrl

    while True:
      try:
        readDHT()
        conn = urllib3.urlopen(tsUrl + tsKey + "&field1=%s&field2=%s" % (T, RH))
        print(conn.read())
        conn.close()
        sleep(12)

      except:
        break

if __name__ == '__main__':
    main()
    
