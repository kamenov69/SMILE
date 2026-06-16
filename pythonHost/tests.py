import sys
import time
import zerorpc
from pykidev import serial_ports_list, search_by_manufacturer, print_my_ip
from pykidev import PykiDev
import numpy as np

#prts = serial_ports_list()
#port = '/dev/ttyACM0'
#ard = PykiDev(port= port, baudrate= 115200)
ard = zerorpc.Client()
#ard.connect("tcp://127.0.0.1:2020")
ard.connect("tcp://192.168.0.216:2020")
print(ard.hello())

time_for_exec = []
number_of_errors = []

for i in range(0, 10000):
    start = time.perf_counter()
    tmp = ard.glo(i)   
    elapsed = time.perf_counter() - start
    time_for_exec.append(elapsed)
    if tmp != i:
        number_of_errors.append(i)
        
        
    time.sleep(0.001)

    
time_for_exec_ms = np.array(time_for_exec) * 1000.0
mean_time_of_exec_ms  = np.mean(time_for_exec_ms)
std_of_time_of_exc_ms = np.std(time_for_exec_ms)
    
print(f' TOE in mS min {np.min(time_for_exec_ms):.2f}',
      f' Mean {mean_time_of_exec_ms:.2f} ',
      f' STD {std_of_time_of_exc_ms:.2f} ',
      f' max {np.max(time_for_exec_ms):.2f} ')
print(f' error numbers {len(number_of_errors)}')
    