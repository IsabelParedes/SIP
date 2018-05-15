################################################################################
#EE 49 - Electronics for the Internet of Things
#Spring 2018 - Final Project
#SMART IRRIGATION PLANT (SIP) by Isabel Paredes
#
#This device periodically measures the water content in the soil by using
#moisture sensors. If the soil measurement is below the threshold, the micro-
#controller waters the plant by turning on a submersible water pump and
#activating a solenoid valve to direct the water to the dry plant.  The device
#also monitors the water level of the reservoir by using two float sensors.  The
#first sensor indicates when the reservoir should be refilled, and the second
#sensor prevents the microcontroller from activating the pump once the water
#level is too low and unsafe to operate.

################################################################################
#Libraries
from machine import Pin, ADC, deepsleep
from board import LED, ADC6, ADC3, A20, A21, A7, A8, A9
from time import sleep
from network import WLAN, STA_IF, mDNS
from mqttclient import MQTTClient

################################################################################
#Defining pins to sensors and actuators

#Moisture sensors output an analog signal which is converted to digital for easy
#maniputation.
moist1 = ADC(Pin(ADC6))      #Green
moist1.atten(ADC.ATTN_11DB)

moist2 = ADC(Pin(ADC3))      #Blue
moist2.atten(ADC.ATTN_11DB)

#Float sensors send a 1 when the switch is open and a 0 when it is closed.
#Open indicates the water is below the level of the sensor.
floRefill = Pin(A20, mode=Pin.IN, pull=Pin.PULL_UP)    #high sensor, yellow
floUnsafe = Pin(A21, mode=Pin.IN, pull=Pin.PULL_UP)    #low sensor, red

#Water pump is activated with a 3V relay
relay = Pin(A7, mode=Pin.OUT)

#Solenoid valves require a 9V battery to open, their circuits are closed by
#using transistors
tran1 = Pin(A9, mode=Pin.OUT)   #Green
tran2 = Pin(A8, mode=Pin.OUT)   #Blue

################################################################################
#Functions

#This function turns on the pump and a solenoid valve to water a single plant.
def water(plant):
    global tran1, tran2, relay

    if plant == 1:
        tran1(1)         #open the solenoid valve for plant 1
        relay(1)         #turn the pump ON
        sleep(10)
        relay(0)         #turn the pump OFF
        tran1(0)         #shut the valve

    elif plant == 2:
        tran2(1)         #open the solenoid valve for plant 2
        relay(1)         #turn the pump ON
        sleep(10)
        relay(0)         #turn the pump OFF
        tran2(0)         #shut the valve


#This function is used to report water reservoir level
def level():
    global floRefill, floUnsafe

    if floUnsafe():
        tank = 0            #reservoir is empty

    elif floRefill():
        tank = 1            #needs a refill

    else:
        tank = 2            #tank is full

    return tank

#This function measures the moisture content in the soil
def soil():
    global moist1, moist2
    small = 1339            #from the sensor calibration results
    big = 2800
    dry1 = []               #lists to hold sensor values
    dry2 = []

    for ii in range(50):    #take multiple measurements to minimize errors
        dry1.append(moist1.read())
        dry2.append(moist2.read())

    dry1 = sum(dry1)/float(len(dry1))     #finding the average
    dry2 = sum(dry2)/float(len(dry2))

    dry1 = 100*(dry1-small)/(big-small)   #normalizing to dryness percentage
    dry2 = 100*(dry2-small)/(big-small)   #>80% is dry - <20% is wet

    return dry1, dry2

################################################################################
#MAIN

watered1 = 0                 #to indicate if plants were watered or not
watered2 = 0
reservoir = level()          #obtain water level
plant1, plant2 = soil()      #get dryness percentage

if reservoir == 0:
    #If the water level is too low, don't do anything
    pass
else:
    if plant1 > 80:          #water plant 1 if dry
        water(1)
        watered1 = 1

    if plant2 > 80:          #water plant 2 if dry
        water(2)
        watered2 = 1


#Connecting to the Internet
wlan = WLAN(STA_IF)
wlan.active(True)
#wlan.connect('EECS-PSK', 'Thequickbrown', 5000)      #name, password
wlan.connect('LMI.net_57de', '00236a7457de', 5000)

for _ in range(20):
    if wlan.isconnected():
        break
    #print("Waiting for Wifi connection...")
    sleep(1)

#print('Wifi connected at', wlan.ifconfig()[0])

#MQTT
tSpeak = 'mqtt.thingspeak.com'            #broker

channelID = '480665'                      #SIP Channel
writeKey = '7PZPPOGEBEHAPKH3'
topic = "channels/" + channelID + "/publish/" + writeKey

#print("Connecting to broker ", tSpeak, "...")
mqtt = MQTTClient(tSpeak)
#print("Connected!")

message = "field1={}&field2={}&field3={}&field4={}&field5={}".format(\
          plant1, plant2, watered1, watered2, reservoir)

#print("Publish TOPIC = {}, MSG = {}".format(topic, message))
mqtt.publish(topic, message)    #publish the message

#print("All done")

mqtt.disconnect()               #close the socket

################################################################################
#Reset
deepsleep(2*60*60*1000)         #to take measurements every 2 hours
