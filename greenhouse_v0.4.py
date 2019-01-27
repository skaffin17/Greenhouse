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

import RPi.GPIO as GPIO
import Adafruit_DHT
from MCP3008 import MCP3008
from RPLCD import CharLCD
import SDL_DS1307
import time
import smbus
import os
import sys
import urllib                 # URL functions
import urllib2                # URL functions

# DEFAULT CONSTANTS
SWITCHGPIO    = 26   # GPIO for switch
INTERVAL      = 2    # Delay between each reading (mins)
AUTOSHUTDOWN  = 1    # Set to 1 to shutdown on switch
tsKey = 'E55K9NU1FSMNEIA7'
tsUrl = 'https://api.thingspeak.com/update'

SETTINGS = {
    "LIGHT_GPIO":       	17,                     # GPIO Number (BCM) for the Relay
    "LIGHT_FROM":       	7,                      # from which time the light can be turned on (hour)
    "LIGHT_UNTIL":      	18,                     # until which time (hour)
    "LIGHT_CHANNEL":    	0,                      # of MCP3008 where the light sensor is connected
    "LIGHT_THRESHOLD":  	500,                    # 
    "DHT_GPIO":         	27,                     # GPIO Number (BCM) of the DHT Sensor
    "DHT_SENSOR":       	Adafruit_DHT.DHT11,     # DHT11 or DHT22
    "TEMP_THRESHOLD":   	27.0,                   # in Celcius
    "HUM_THRESHOLD":		80.0,			# in percent
    "SERVO_GPIO":       	22,                     # GPIO Number (BCM), which opens the window
    "SERVO_OPEN_ANGLE": 	90.0,                  	# degrees by which the servo will turn to open the window
    "MOISTURE_CHANNELS":	[1, 2],     		# of MCP3008 where the sensors are connected
    "MOISTURE_THRESHOLD":   	450,        		# average value of the 
    "WATER_PUMP_GPIO":      	23,         		# GPIO Number (BCM) for the water pump relay input
    "WATERING_TIME":        	10,         		# length of time, in seconds, that the water pump is turned on
    "WATER_START":		7			# hour when watering occurs 
}

# Enable shutdown button
def switchCallback(channel):

  global AUTOSHUTDOWN

  # Called if button is pressed
  if AUTOSHUTDOWN==1:
    os.system('/sbin/shutdown -h now')
  sys.exit(0)


# Read date and time
def readTime():
    try:
        ds1307 = SDL_DS1307.SDL_DS1307(1, 0x68)
        return ds1307.read_datetime()
    except:
        # alternative: return the system-time:
        return datetime.datetime.utcnow()


# Read temperature and pressure
def readDHT():
    temp, hum = Adafruit_DHT.read_retry(11, SETTINGS["DHT_GPIO"])
    if temp is not None and hum is not None:
       print('Temp={0:0.1f}*C Hum={1:0.1f}%'.format(temp, hum))
    else:
       print("Unable to read from DHT")
    # Display values on LCD screen
    lcd = CharLCD(cols=16, rows=2, pin_rs=5, pin_e=6, pins_data=[33, 35, 37, 23])
    while True:
        lcd.cursor_pos = (0, 0)
        lcd.write_string("Temp: %d C" % temp)
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Hum: %d %%" % hum)


# Read light sensor
def readLight():
    while True:
        adc = MCP3008()
        # read 10 times to avoid measuring errors
        light = 0
        for i in range(10):
            light += adc.read( channel = SETTINGS["LIGHT_CHANNEL"] )
        light /= 10.0

    if light is not None:
        print('Light={0:0.1f}'.format(light))
    else:
        print("Unable to read from light sensor")


# Read soil moisture sensors
def readMoisture():
    while True:
      adc = MCP3008()
      soil = 0
      for ch in "MOISTURE_CHANNELS":

      # read 10 times to avoid measuring errors
        v = 0
      for i in range(10):
        v += adc.read( channel = ch )
      v /= 10.0
      soil += v
      soil /= float(len("MOISTURE_CHANNELS"))

    if soil is not None:
        print('SoilMoisture={0:0.1f}'.format(soil))
    else:
        print("Unable to read from soil moisture sensors")


   
# Post data to Thingspeak
def sendData(url,key,field1,field2,field3,field4,temp,humi,light,soil):
  """
  Send event to internet site
  """

  values = {'api_key' : key,'field1' : temp,'field2' : hum, 'field3' : light, 'field4' : soil}

  postdata = urllib.urlencode(values)
  req = urllib2.Request(url, postdata)

  log = time.strftime("%d-%m-%Y,%H:%M:%S") + ","
  log = log + "{:.1f}C".format(temp) + ","
  log = log + "{:.2f}%%".format(humid) + ","
  log = log + "{:.3f}".format(light) + ","
  log = log + "{:.4f}".format(soil) + ","

  try:
    # Prepare data to Thingspeak
    response = urllib2.urlopen(req, None, 5)
    html_string = response.read()
    response.close()
    log = log + 'Update ' + html_string

  except urllib2.HTTPError as e:
    log = log + 'Server could not fulfill the request. Error code: ' + e.code
  except urllib2.URLError as e:
    log = log + 'Failed to reach server. Reason: ' + e.reason
  except:
    log = log + 'Unknown error'

  print(log)


# Control the led grow lights
def controlLight():
    timestamp = readTime()
        
    if SETTINGS["WATER_START"] <= timestamp.hour:
        # check light sensors
        adc = MCP3008()
        # read 10 times to avoid measuring errors
        value = 0
        for i in range(10):
            value += adc.read( channel = SETTINGS["LIGHT_CHANNEL"] )
        value /= 10.0
        
        if value <= SETTINGS["LIGHT_THRESHOLD"]:
            # turn light on
            GPIO.setup(SETTINGS["LIGHT_GPIO"], GPIO.OUT, initial=GPIO.LOW) # Relay LOW = ON
        else:
            # turn light off
            GPIO.setup(SETTINGS["LIGHT_GPIO"], GPIO.OUT, initial=GPIO.HIGH)
    else:
        # turn light off
        GPIO.setup(SETTINGS["LIGHT_GPIO"], GPIO.OUT, initial=GPIO.HIGH)


# Control the water pump
def controlWater():
    # read moisture
    adc = MCP3008()
    value = 0
    for ch in "MOISTURE_CHANNELS":
        # read 10 times to avoid measuring errors
        v = 0
        for i in range(10):
            v += adc.read( channel = ch )
        v /= 10.0
        value += v
        
    value /= float(len("MOISTURE_CHANNELS"))
        
    if value > "MOISTURE_THRESHOLD":
        # turn pump on for some seconds
        GPIO.setup("WATER_PUMP_GPIO", GPIO.OUT, initial=GPIO.LOW)
        time.sleep("WATERING_TIME")
        GPIO.output("WATER_PUMP_GPIO", GPIO.HIGH)


# Control the servo to open the top vent
def controlVent():
    temperature, humidity = Adafruit_DHT.read_retry(SETTINGS["DHT_SENSOR"], SETTINGS["DHT_GPIO"])
    
    GPIO.setup(SETTINGS["SERVO_GPIO"], GPIO.OUT)
    pwm = GPIO.PWM(SETTINGS["SERVO_GPIO"], 50)
    
    if temperature > SETTINGS["TEMP_THRESHOLD"]:
        # open window
        angle = float(SETTINGS["SERVO_OPEN_ANGLE"]) / 20.0 + 2.5
        pwm.start(angle)

    elif humidity > SETTINGS["HUMIDITY_THRESHOLD"]:
	# open window
        angle = float(SETTINGS["SERVO_OPEN_ANGLE"]) / 20.0 + 2.5
        pwm.start(angle)

    else:
        # close window
        pwm.start(2.5)
    # save current
    time.sleep(2)
    pwm.ChangeDutyCycle(0)


# Main function
def main():

    global SWITCHGPIO
    global INTERVAL
    global AUTOSHUTDOWN
    global tsKey
    global tsUrl

    # Setup GPIO
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Switch on GPIO26 as input pulled LOW by default
    GPIO.setup(SWITCHGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
    # Define what function to call when switch pressed
    GPIO.add_event_detect(SWITCHGPIO, GPIO.RISING, callback=switchCallback)

    #  Execute functions
    try:
        while True:
            readDHT()
            sendData(tsUrl,tsKey,'field1','field2','field3','field4',temp,hum,light,soil)
            sys.stdout.flush()
            
        time.sleep (INTERVAL*60)
  
    except :
        # Reset GPIO settings
        GPIO.cleanup()

if __name__=="__main__":
   main()
