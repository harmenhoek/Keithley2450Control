import numpy as np
import time

target_voltage = 3  # in Volts
steps = 5  # int number of steps
pause = 1  # pause in seconds

voltages = iter(np.linspace(0, target_voltage, steps))

t_start = time.time()


while True:
    if time.time() - t_start > pause:
        print(next(voltages, None))
        t_start = time.time()