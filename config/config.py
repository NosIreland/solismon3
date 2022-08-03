INVERTER_SERIAL = 123456789   # WiFi stick serial number
INVERTER_IP = "192.168.1.55"  # IP address of inverter
INVERTER_PORT = 8899          # Port number
MQTT_SERVER = "192.168.1.20"  # IP address of MQTT server
MQTT_PORT = 1883              # Port number of MQTT server
MQTT_SERVER_USER = "mqtt"     # MQTT server username
MQTT_SERVER_PASSWORD = "1234" # MQTT server password
MQTT_TOPIC = "solis/METRICS"  # MQTT topic to use
CHECK_INTERVAL = 30           # How often to check(seconds), only applies when 'PROMETHEUS = False' otherwise uses Prometheus scrape interval
MQTT_KEEPALIVE = 60           # MQTT keepalive
PROMETHEUS = False            # Enable Prometheus exporter
PROMETHEUS_PORT = 18000       # Port to use for Prometheus exporter
MODIFIED_METRICS = True       # Enable modified metrics
DEBUG = False                 # Enable debugging, helpfull to diagnose problems
