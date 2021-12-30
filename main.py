import config
import registers
import logging
import paho.mqtt.client as mqtt
from sys import exit
from time import strptime, mktime, sleep
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from pysolarmanv5.pysolarmanv5 import PySolarmanV5

# How often to check(does not apply on prometheus)
metrics_list = []
debug = 0


def add_modified_metrics(met_pwr_1, met_pwr_2, house_pwr, bypass_pwr, solar_pwr, batt_dir, batt_pwr):
    global metrics_list
    met_pwr = met_pwr_1 - met_pwr_2
    total_load = house_pwr + bypass_pwr
    solar_to_house = solar_pwr - total_load

    # Present battery modified metrics
    if batt_dir == 0:
        metrics_list.append(['battery_power_modified', 'Battery Power(modified)', batt_pwr])
        metrics_list.append(['battery_power_in_modified', 'Battery Power In(modified)', batt_pwr])
        metrics_list.append(['battery_power_out_modified', 'Battery Power Out(modified)', 0])
        metrics_list.append(['grid_to_battery_power_in_modified', 'Grid to Battery Power In(modified)', 0])
    if batt_dir == 1:
        metrics_list.append(['battery_power_modified', 'Battery Power(modified)', batt_pwr * -1])
        metrics_list.append(['battery_power_out_modified', 'Battery Power Out(modified)', batt_pwr])
        metrics_list.append(['battery_power_in_modified', 'Battery Power In(modified)', 0])
        metrics_list.append(['grid_to_battery_power_in_modified', 'Grid to Battery Power In(modified)', 0])
    if total_load < met_pwr and batt_pwr > 0:
        metrics_list.append(['grid_to_battery_power_in_modified', 'Grid to Battery Power In(modified)', batt_pwr])

    # Present meter modified metrics
    if met_pwr >= 0:
        metrics_list.append(['meter_power_in_modified', 'Meter Power In(modified)', met_pwr])
        metrics_list.append(['meter_power_modified', 'Meter Power(modified)', met_pwr])
        metrics_list.append(['meter_power_out_modified', 'Meter Power Out(modified)', 0])
    if met_pwr <= 0:
        metrics_list.append(['meter_power_out_modified', 'Meter Power Out(modified)', met_pwr * -1])
        metrics_list.append(['meter_power_in_modified', 'Meter Power In(modified)', 0])
        metrics_list.append(['meter_power_modified', 'Meter Power(modified)', met_pwr])

    # Present load modified metrics
    metrics_list.append(['total_load_power_modified', 'Total Load Power(modified)', total_load])
    if solar_to_house > 0:
        metrics_list.append(['solar_to_house_power_modified', 'Solar To House Power(modified)', solar_to_house])
    if solar_to_house <= 0:
        metrics_list.append(['solar_to_house_power_modified', 'Solar To House Power(modified)', 0])

    logging.info('Added modified metrics')


def scrape_solis(debug):
    global metrics_list
    metrics_list = []
    try:
        logging.info('Connecting to MODBUS Server')
        modbus = PySolarmanV5(
            config.INVERTER_IP, config.INVERTER_SERIAL, port=config.INVERTER_PORT, mb_slave_id=1, verbose=debug)
    except Exception as e:
        logging.error('Could not connect to Inverter MODBUS', repr(e))

    logging.info('Scraping...')

    for r in registers.all_regs:
        reg = r[0]
        reg_len = len(r[1])
        reg_des = r[1]

        # Sometimes the query fails this will retry it forever(probably needs counter)
        while True:
            try:
                # read registers at address , store result in regs list
                regs = (modbus.read_input_registers(register_addr=reg, quantity=reg_len))

            except Exception as e:
                logging.error('Cannot read registers: ', repr(e))
                continue
            break
        logging.info("register address #" + str(reg) + " length " + str(reg_len))

        # Convert time to epoch
        if reg == 33022:
            inv_year = '20' + str(regs[0]) + '-'
            if regs[1] < 10:
                inv_month = '0' + str(regs[1]) + '-'
            else:
                inv_month = str(regs[1]) + '-'
            if regs[2] < 10:
                inv_day = '0' + str(regs[2]) + ' '
            else:
                inv_day = str(regs[2]) + ' '
            if regs[3] < 10:
                inv_hour = '0' + str(regs[3]) + ':'
            else:
                inv_hour = str(regs[3]) + ':'
            if regs[4] < 10:
                inv_min = '0' + str(regs[4]) + ':'
            else:
                inv_min = str(regs[4]) + ':'
            if regs[5] < 10:
                inv_sec = '0' + str(regs[5])
            else:
                inv_sec = str(regs[5])
            inv_time = inv_year + inv_month + inv_day + inv_hour + inv_min + inv_sec
            print('Inverter time: ' + inv_time)
            time_tuple = strptime(inv_time, '%Y-%m-%d %H:%M:%S')
            time_epoch = mktime(time_tuple)
            metrics_list.append(['system_epoch', 'System Epoch Time', time_epoch])

        # Add metric to list
        for (i, item) in enumerate(regs):
            if reg_des[i][0] != 'not_used':
                metrics_list.append([reg_des[i][0], reg_des[i][1], item])

                # Get battery metric for modification
                if reg_des[i][0] == 'battery_power_2':
                    batt_pwr = item
                if reg_des[i][0] == 'battery_current_direction':
                    batt_dir = item

                # Get grid metric for modification
                if reg_des[i][0] == 'meter_active_power_1':
                    met_pwr_1 = item
                if reg_des[i][0] == 'meter_active_power_2':
                    met_pwr_2 = item

                # Get load metric for modification
                if reg_des[i][0] == 'house_load_power':
                    house_pwr = item
                if reg_des[i][0] == 'bypass_load_power':
                    bypass_pwr = item
                if reg_des[i][0] == 'total_dc_input_power_2':
                    solar_pwr = item

    add_modified_metrics(met_pwr_1, met_pwr_2, house_pwr, bypass_pwr, solar_pwr, batt_dir, batt_pwr)

    logging.info('Scraped')


def publish_mqtt():
    try:
        logging.info('Connecting to MQTT Server')
        mqttc = mqtt.Client()
        mqttc.connect(config.MQTT_SERVER, config.MQTT_PORT, config.MQTT_KEEPALIVE)
        mqttc.on_connect = logging.info("Connected to MQTT " + str(config.MQTT_SERVER) + ":" + str(config.MQTT_PORT))

        if not config.PROMETHEUS:
            scrape_solis(debug)
        for metric in metrics_list:
            mqttc.publish(config.MQTT_TOPIC + '/' + str(metric[0]), metric[2])

        mqttc.disconnect()
    except Exception as e:
        logging.error('Could not connect to MQTT', repr(e))


class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        scrape_solis(debug)

        for metric in metrics_list:
            yield GaugeMetricFamily(metric[0], metric[1], value=metric[2])
        publish_mqtt()


if __name__ == '__main__':
    try:
        if config.DEBUG:
            logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
            debug = 1
        else:
            logging.basicConfig(level=logging.WARN, handlers=[logging.StreamHandler()])
            debug = 0

        logging.info('Starting')

        if config.PROMETHEUS:
            logging.info('Starting Web Server')
            start_http_server(18000)

            REGISTRY.register(CustomCollector())
            while True:
                sleep(config.CHECK_INTERVAL)

        else:
            while True:
                publish_mqtt()
                sleep(config.CHECK_INTERVAL)

    except Exception as e:
        logging.error('Cannot start: ', repr(e))
        exit(1)
