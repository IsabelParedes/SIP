This device periodically measures the water content in the soil by using moisture sensors. If the soil measurement is below the threshold, the microcontroller waters the plant by turning on a submersible water pump and activating a solenoid valve to direct the water to the dry plant.  The device also monitors the water level of the reservoir by using two float sensors.  The first sensor indicates when the reservoir should be refilled, and the second sensor prevents the microcontroller from activating the pump once the water level is too low and unsafe to operate.

## Materials
* ESP32 - Huzzah
* Float sensors
* Capacitive moisture sensor
* 3V Relay
* Water pump
* Transistors
* Resistors
* LEDs
* Solenoid valves
* 9V battery
* Water tank
* 2-way valve
* Tubing

## Setup
* [Circuit Diagram](https://github.com/iparedes314/SIP/blob/master/Circuit%20Diagram.jpg)

## Code
* [Main](https://github.com/iparedes314/SIP/blob/master/main.py)

## Authors

* **Isabel Paredes**
