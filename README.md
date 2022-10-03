# SolisMon3

This is 3rd iteration of my Solis Inverter monitor. 
This is based on great work by [jmccrohan](https://github.com/jmccrohan/pysolarmanv5)

The data is pulled directly from Solis WiFi stick. You need to provide serial number and IP address of the stick.   
Metrics are published to MQTT and Prometheus, or just MQTT.   
The registers to be polled and their meaning are stored in `registers.py` file. I have populated file already with registers that I use. The list is not final but shoudl be good enough for most cases.

## Configuration
### config.py
Modify the values in [config.py](./config/config.py) to match your setup
```
INVERTER_SERIAL = 123456789   # WiFi stick serial number
INVERTER_IP = "192.168.1.55"  # IP address of inverter
INVERTER_PORT = 8899          # Port number
MQTT_SERVER = "192.168.1.20"  # IP address of MQTT server
MQTT_PORT = 1883              # Port number of MQTT server
MQTT_TOPIC = "solis/METRICS"  # MQTT topic to use
MQTT_USER = "foo"             # MQTT auth user (blank to disable auth)
MQTT_PASS = "bar"             # MQTT auth password
CHECK_INTERVAL = 30           # How often to check(seconds), only applies when 'PROMETHEUS = False' otherwise uses Prometheus scrape interval
MQTT_KEEPALIVE = 60           # MQTT keepalive
PROMETHEUS = False            # Enable Prometheus exporter
PROMETHEUS_PORT = 18000       # Port to use for Prometheus exporter
MODIFIED_METRICS = True       # Enable modified metrics
DEBUG = False                 # Enable debugging, helpfull to diagnose problems
```

MODIFIED_METRICS create additional metrics. It takes multiple existing metrics and creates single metric out of them.   
This is useful for me as I do not need to make modifications later in Home-assistant using templates and/or Grafana.
In Home-assistant this allows me easy integration with custom cards like 
[tesla-style-solar-power-card](https://github.com/reptilex/tesla-style-solar-power-card)

```
battery_power_modified
battery_power_in_modified
battery_power_out_modified
grid_to_battery_power_in_modified
meter_power_in_modified
meter_power_modified
meter_power_out_modified
total_load_power_modified
solar_to_house_power_modified
```

### registers.py
I have registers predefined for single phase Solis RHI 4G hybrid inverter in [registers.py](./config/registers.py) file. 
The register mappings are not the same on all inverters. Non-hybrid inverters have different mapping, so you will need to adjust. 
I will try to add more later on.   
The registers are read in blocks as that is much faster than reading individual registers one by one.    
In registers.py you need to provide:   
Register number you want to start with(integer), register name(string, no space allowed, use '_'), register description(string)   
Add '*' in front of register name if you want it to be skipped. 

## Running
Run main.py

### Running in docker
Docker images is provided.   
On your docker host create a folder solismon3/config and copy your modified config.py and registers.py files in there
```
docker run -it -d --restart unless-stopped --name solismon3 -v /solismon3/config:/solismon3/config -p 18000:18000 nosireland/solismon3
```

### Docker Compose example
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

### Testing
To see if it is running properly I would advise enabling debugging `DEBUG = False` and also `PROMETHEUS = True`
(you do not need to have Prometheus installed) for testing. Once started check container logs `docker logs solismon3` and in 
browser enter url http://docker_host_ip:18000. Assuming all is ok, you should see metrics in browser. 

If program fails with default [registers.py](./config/registers.py) you can try scanning registers with 
[register_scan](./examples/register_scan.py) and see if you can get anything. For non-hybrid inverter start with 1000 and go up.

## Important
This is a very early draft version and things might not work as expected. Feel free to ask questions.
