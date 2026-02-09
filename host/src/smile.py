    

import time, sys 
import zerorpc
from pykiba import serial_ports_list, search_by_manufacturer, get_my_ip, print_my_ip
from pykiba import PykiDev
#from tenacity import retry, stop_after_attempt, wait_fixed


#@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def start_server( com_port = None , baudrate = 115200, name = None,  n = None, bind_port=2020): # Debug version
    """
    Starts a Zerorpc server of a pykiDev object or returns this object.
    
    Parameters
    ----------
    com_port : 
        DESCRIPTION: Comport device or path, string,
        Defaul: None.
    
    baudrate : 
        DESCRIPTION: Baudrate of Arduino UART, int
        Default: 115200.
    
    name : 
        DESCRIPTION: Comport name from its driver, string
        Default: None.
        
    n : 
        DESCRIPTION: Number of the comport in the printed list,int
        Default: None.
    
    bind_port : 
        Zerorpc's network port, int
        DESCRIPTION: The default is None.

    Returns
    -------
    if not bind_port: definet returns a pykiDev object.
    else: starts a zerorpc server of a pykiDev object,

    """
    print(f'{n=}, {name=}, {com_port=}, {baudrate=  }, {bind_port= } ' )
    prts = serial_ports_list()
    if n != None:
        prt_device = prts[n].device 
    
    elif com_port != None:
        prt_device = com_port
    
    elif name != None:
        prt_device = search_by_manufacturer(prts,name)
    
    else:
        raise ConnectionError(" Port not definet")   
    
        
    print(f"Opening: {prt_device} @ baudrate: {baudrate}")

    ard = PykiDev(prt_device, baudrate )
    print("Testing ... ")
    print(f'Arduino responsed on hello with: {ard.hello()}') 
    print(f'Set mode to: {ard.mode(1)}')
    
    if bind_port == None:
        return ard
    else:
        del ard
        time.sleep(3)
        
        print("The zerorpc server's starting on: ")
        print_my_ip()
        print( f":{bind_port}")
        s = zerorpc.Server(PykiDev(prt_device, baudrate ))
        s.bind(f"tcp://0.0.0.0:{bind_port}")
        print("The zerorpc server's runing!")
        s.run()
        
    
  
     
if __name__ == "__main__":
    import fire
    fire.Fire(start_server)
    #ard = start_server(n = 1, bind_port=2020)
