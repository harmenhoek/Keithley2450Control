import numpy as np
import time

target_voltage = 3  # in Volts
steps = 5  # int number of steps
pause = 1  # pause in seconds

RampBack = True

voltages = np.linspace(0, target_voltage, steps)
if RampBack:
    voltages = np.append(voltages, voltages[::-1])

print(voltages)