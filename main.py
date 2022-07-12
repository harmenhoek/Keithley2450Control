# import pymeasure  # need to import whole library, otherwise pyinstaller fails
from pymeasure.instruments.keithley import Keithley2450
from datetime import datetime
import time
from mariobeep import mariobeep
import keyboard
import numpy as np

readout_rate = 1.0  # frequency in hz

target_voltage = 3  # in Volts
steps = 10  # int number of steps
pause = 3  # pause in seconds

import pyvisa

rm = pyvisa.ResourceManager()  # should use Keysight by default
print(rm.list_resources())

try:
    keithley = Keithley2450('USB0::0x05E6::0x2450::04456958::INSTR')
    # mariobeep(keithley)

    keithley.reset()
    keithley.use_front_terminals()
    keithley.measure_current()
    keithley.enable_source()

    # keithley.apply_voltage()

    keithley.config_buffer(points=100)
    keithley.start_buffer()
except:
    raise ConnectionError("Unable to connect to the Keithley 2450.")


def ReadOutToLogFile(f, setvoltage):
    datetimestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f"{datetimestamp}, {keithley.mean_current}, {keithley.mean_voltage}, {setvoltage}")
    f.write(f"{datetimestamp}, {keithley.mean_current}, {keithley.mean_voltage}, {setvoltage}\n")
    keithley.reset_buffer()
    keithley.start_buffer()


# voltages = iter(np.linspace(0, target_voltage, steps))
setvoltage = None
voltages = np.linspace(0, target_voltage, steps)

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

        if ramping and (time.time() - t_start_2 > pause):
            if cntr < len(voltages):
                setvoltage = voltages[cntr]
                # setvoltage = next(voltages, None)
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

'''
keithley.enable_source()                # Enables the source output
target_voltage = 3
steps = 10
pause = 1
keithley.ramp_to_voltage(target_voltage, steps, pause)


'''
