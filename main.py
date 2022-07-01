import pymeasure  # need to import whole library, otherwise pyinstaller fails
# from pymeasure.instruments.keithley import Keithley2450
from datetime import datetime
import time
from mariobeep import mariobeep


readout_rate = 1.0  # frequency in hz

import pyvisa
rm = pyvisa.ResourceManager()  # should use Keysight by default
print(rm.list_resources())


try:
    # keithley = Keithley2450('ASRL3::INSTR')
    keithley = pymeasure.instruments.keithley.Keithley2450('USB0::0x05E6::0x2450::04456958::INSTR')
    keithley.measure_current()
    keithley.measure_voltage()
    mariobeep(keithley)
except:
    raise ConnectionError("Unable to connect to the Keithley 2450.")


def ReadOutToLogFile(f):
    datetimestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f"{datetimestamp}, {keithley.current}, {keithley.voltage}")
    f.write(f"{datetimestamp}, {keithley.current}, {keithley.voltage}\n")

datetimestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"Keithley_Logfile_{datetimestamp}.csv"
with open(filename, 'w') as f:
    f.write("datetimestamp, current (A), voltage (V)\n")
    print(f"Created log file '{filename}'.")
    t_start = time.time()
    while True:
        if time.time() - t_start > readout_rate:
            try:
                ReadOutToLogFile(f)
            except Exception as e:
                print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' + str(e))
            t_start = time.time()


'''
keithley.enable_source()                # Enables the source output
target_voltage = 3
steps = 10
pause = 1
keithley.ramp_to_voltage(target_voltage, steps, pause)
  
            
'''
