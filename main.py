# import pymeasure  # need to import whole library, otherwise pyinstaller fails
from pymeasure.instruments.keithley import Keithley2450
from datetime import datetime
import time
from mariobeep import mariobeep
import keyboard
import numpy as np
import pyvisa

# ----------------------- SETTINGS ---------------------

readout_rate = 1.0  # read out frequency in hz

Ramping = False  # allows to ramp to a target_voltage in steps, dwelling dwell_time at each step.
target_voltage = 3  # in volts
steps = 10  # int number of steps
dwell_time = 3  # pause in seconds
RampBack = True  # ramps back to 0 with same steps and dwell_time at the end

CustomRange = True  # set a custom range of voltages and dwell times.
voltage_range = [0, 3, 0]  # in volts
dwell_time = [10, 60, 10]  # in seconds

# ----------------------- Don't make changes below here ---------------------

if Ramping is True and CustomRange is True:
    raise AttributeError("'Ramping' and 'CustomRange' cannot both be True.")
elif Ramping is False and CustomRange is False:
    raise AttributeError("'Ramping' and 'CustomRange' cannot both be False.")


rm = pyvisa.ResourceManager()  # should use Keysight by default
print(rm.list_resources())

try:
    keithley = Keithley2450('USB0::0x05E6::0x2450::04456958::INSTR')
    # mariobeep(keithley)

    keithley.reset()
    keithley.use_front_terminals()
    keithley.measure_current()
    keithley.enable_source()

    # keithley.config_buffer(points=100)
    # keithley.start_buffer()
except:
    raise ConnectionError("Unable to connect to the Keithley 2450.")


def ReadOutToLogFile(f, setvoltage):
    datetimestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    # print(f"{datetimestamp}, {keithley.mean_current}, {keithley.mean_voltage}, {setvoltage}")
    # f.write(f"{datetimestamp}, {keithley.mean_current}, {keithley.mean_voltage}, {setvoltage}\n")
    print(f"{datetimestamp}, {keithley.current}, {keithley.voltage}, {setvoltage}")
    f.write(f"{datetimestamp}, {keithley.current}, {keithley.voltage}, {setvoltage}\n")
    # keithley.reset_buffer()
    # keithley.start_buffer()

setvoltage = None

if Ramping:
    voltages = np.linspace(0, target_voltage, steps)
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