# import pymeasure  # need to import whole library, otherwise pyinstaller fails
from pymeasure.instruments.keithley import Keithley2450
from datetime import datetime
import time
from mariobeep import mariobeep
import keyboard
import numpy as np
import pyvisa
import os
import json
from json_minify import json_minify  # allows for comments in json

config_path = 'config.json'

if not os.path.isfile(config_path):
    raise FileNotFoundError("config.json is not found.")

with open(config_path, 'r') as f:
    config_raw = f.read()

config = json.loads(json_minify(config_raw))

readout_rate = config['readout_rate']  # read out frequency in hz

if config['mode'] == 'ramping':
    Ramping = True
    CustomRange = False
    target_voltage = config['ramping_settings']['target_voltage']  # in volts
    start_voltage = config['ramping_settings']['start_voltage']  # in volts
    steps = config['ramping_settings']['steps']  # int number of steps
    dwell_time = config['ramping_settings']['dwell_time']  # pause in seconds
    RampBack = config['ramping_settings']['rampback']  # ramps back to 0 with same steps and dwell_time at the end
elif config['mode'] == 'custom':
    Ramping = False
    CustomRange = True
    voltage_range = config['custom_settings']['voltage_range']  # in volts
    dwell_time = config['custom_settings']['dwell_time']  # in seconds
else:
    raise AttributeError("No correct 'mode' selected. Use 'ramping' or 'custom'.")


print("Keithley2450Control program")

print('Checking available devices ...')

rm = pyvisa.ResourceManager()  # should use Keysight by default
print(f"Found devices: {rm.list_resources()}. Needs device {config['advanced_settings']['device_id']}")

try:
    keithley = Keithley2450(config['advanced_settings']['device_id'])
    print('Connection successfull.')
    if config['mario']:
        mariobeep(keithley)

    keithley.reset()
    if config['advanced_settings']['front_terminals']:
        keithley.use_front_terminals()
    keithley.measure_current()
    keithley.enable_source()
    print('Keithley setup correctly.')

    # keithley.config_buffer(points=100)
    # keithley.start_buffer()
except:
    raise ConnectionError("Unable to connect to the Keithley 2450.")


def ReadOutToLogFile(f, setvoltage):
    datetimestamp = datetime.now().strftime(config['advanced_settings']['datetime_format'])
    # print(f"{datetimestamp}, {keithley.mean_current}, {keithley.mean_voltage}, {setvoltage}")
    # f.write(f"{datetimestamp}, {keithley.mean_current}, {keithley.mean_voltage}, {setvoltage}\n")
    print(f"{datetimestamp}, {keithley.current}, {keithley.voltage}, {setvoltage}")
    f.write(f"{datetimestamp}, {keithley.current}, {keithley.voltage}, {setvoltage}\n")
    # keithley.reset_buffer()
    # keithley.start_buffer()

setvoltage = None

if Ramping:
    voltages = np.linspace(start_voltage, target_voltage, steps)
    dwell_time = np.ones_like(voltages) * dwell_time
    if RampBack:
        voltages = np.append(voltages, voltages[-2::-1])

if CustomRange:
    voltages = voltage_range


datetimestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"Keithley_Logfile_{datetimestamp}.csv"
with open(filename, 'w') as f:
    f.write("datetimestamp, current (A), voltage (V), set voltage (V)\n")
    print(f"Created log file '{filename}'.")
    t_start = time.time()
    t_start_2 = time.time()
    ramping = False
    loop = True
    cntr = 0
    print("  Start voltage sweep by pressing 'a' (long press might be needed).\n  Stop code by pressing 'ESC'.")
    while loop:

        # Log
        if time.time() - t_start > readout_rate:
            try:
                ReadOutToLogFile(f, setvoltage)
            except Exception as e:
                print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' + str(e))
            t_start = time.time()

        # Ramp voltage on enter press
        if ramping is False and keyboard.is_pressed("a"):
            ramping = True
            print(f'Ramping started with voltages: {voltages}.')

        if ramping and (time.time() - t_start_2 > dwell_time[cntr]):
            if cntr < len(voltages):
                setvoltage = voltages[cntr]
                print(f'Voltage set to {setvoltage}V.')
                keithley.source_voltage = setvoltage
                keithley.current
                t_start_2 = time.time()
                cntr = cntr + 1
            else:
                print('Voltage ramping ended')
                ramping = False

        if keyboard.is_pressed("esc"):
            print('Stopping now!')
            keithley.shutdown()
            loop = False

print('Program terminated successfully. Bye!')