#!/usr/bin/env python
#encoding: utf-8

# Based on code from Felix Stern, Matt Hawkins
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
import SDL_DS1307
from time import sleep
import urllib2                # URL functions

# THINKSPEAK ACCOUNT
tsKey = 'E55K9NU1FSMNEIA7'
tsUrl = 'https://api.thingspeak.com/update'


# Read temperature and pressure
def readDHT():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 27)
    # return dict
    return (str(RH), str(T))
    

# Main function
def main():

    global tsKey
    global tsUrl

    #  Execute functions
    if len(sys.argv) < 2:
      print('Usage: python tstest.py tsKey')
      exit(0)
    print('starting...')

    baseURL = 'https://api.thingspeak.com/update?api_key=%s' % sys.argv[1]

    while True:
      try:
        RH, T = readDHT()
        f = urllib2.urlopen(baseURL + "&field1=%s&field2=%s" % (RH,T))
        print(f.read())
        f.close()
        sleep(15)
      except:
        print('exiting.')
        break

  
if __name__=="__main__":
   main()
