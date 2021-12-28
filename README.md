# SolisMon3

This is 3rd iteration of my Solis Inverter monitor. 
This is based on great work by [jmccrohan](https://github.com/jmccrohan/pysolarmanv5)

The data is pulled directly from Solis WiFi stick. You need to provide serial number and IP address of the stick.
Metrics are published to MQTT and Prometheus, or just MQTT
The polled registers and their meaning are stored in registers.py file. The list is not final. 

## Installation
Modify the values in config.py and run main.py  
Or you can build docker image

## Important
This is a very early draft version and things might not work as expected but when they do yoh should see 