# SolisMon3

This is 3rd iteration of my Solis Inverter monitor. 
This is based on great work by [jmccrohan](https://github.com/jmccrohan/pysolarmanv5)

The data is pulled directly from Solis WiFi stick. You need to provide serial number and IP address of the stick.
Metrics are published to MQTT and Prometheus, or just MQTT
The polled registers and their meaning are stored in registers.py file. The list is not final. 

## Installation
Modify the values in config.py and run main.py  

## Running in docker
```
docker run -it -d --restart unless-stopped --name solismon3 -v /solismon3/config:/solismon3/config -p 18000:18000 nosireland/solismon3
```

## Docker Compose example
```
version: "3.4"

services:
  solismon3:
    image: nosireland/solismon3:latest
    container_name: solismon3
    restart: always
    ports:
      - 18000:18000
    volumes:
      - /solismon3/config:/solismon3/config
    logging:
      options:
        max-size: 5m
```
## Important
This is a very early draft version and things might not work as expected but when they do yoh should see 