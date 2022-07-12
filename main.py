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
    # keithley = Keithley2450('ASRL3::INSTR')
    # keithley = pymeasure.instruments.keithley.Keithley2450('USB0::0x05E6::0x2450::04456958::INSTR')
    keithley = Keithley2450('USB0::0x05E6::0x2450::04456958::INSTR')
    keithley.measure_current()
    keithley.measure_voltage()
    keithley.enable_source()  # Enables the source output
    # mariobeep(keithley)
except:
    raise ConnectionError("Unable to connect to the Keithley 2450.")


def ReadOutToLogFile(f, setvoltage):
    datetimestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f"{datetimestamp}, {keithley.current}, {keithley.voltage}, {setvoltage}")
    f.write(f"{datetimestamp}, {keithley.current}, {keithley.voltage}, {setvoltage}\n")



voltages = iter(np.linspace(0, target_voltage, steps))
setvoltage = None

datetimestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"Keithley_Logfile_{datetimestamp}.csv"
with open(filename, 'w') as f:
    f.write("datetimestamp, current (A), voltage (V), set voltage (V)\n")
    print(f"Created log file '{filename}'.")
    t_start = time.time()
    t_start_2 = time.time()
    ramping = False
    while True:

        # Log
        if time.time() - t_start > readout_rate:
            try:
                ReadOutToLogFile(f, setvoltage)
            except Exception as e:
                print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' + str(e))
            t_start = time.time()

        # Ramp voltage on enter press
        if keyboard.read_event() == "enter":
            ramping = True
            t_start_2 = time.time()

        if ramping and (time.time() - t_start_2 > pause):
            setvoltage = next(voltages, None)
            if setvoltage:
                keithley.apply_voltage(setvoltage)
                t_start_2 = time.time()
            else:
                print('Voltage ramping ended')
                ramping = False



'''
keithley.enable_source()                # Enables the source output
target_voltage = 3
steps = 10
pause = 1
keithley.ramp_to_voltage(target_voltage, steps, pause)
  
            
'''
