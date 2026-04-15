import sys
import zerorpc
from pykidev import serial_ports_list, search_by_manufacturer, print_my_ip
from pykidev import PykiDev


def start_server(comport=None, baudrate=9600, name=None, n=None, bind_port=2020):
    """
    Starts a ZeroRPC server for a PykiDev object or returns the object directly.

    Parameters
    ----------
    comport : str, optional
        Serial device path, for example '/dev/ttyACM0' or 'COM3'.
        Default: None.

    baudrate : int, optional
        Arduino UART baud rate.
        Default: 9600.

    name : str, optional
        Prefix of the USB manufacturer name used to find the serial port.
        Default: None.

    n : int, optional
        Index of the serial port in the printed port list.
        Default: None.

    bind_port : int, optional
        Network port for the ZeroRPC server.
        If None, the function returns the PykiDev object instead of starting a server.
        Default: None.

    Returns
    -------
    PykiDev
        If bind_port is None, returns an initialized PykiDev object.

    Otherwise
    ---------
    Starts a ZeroRPC server and blocks.
    """
    print(f"{n=}, {name=}, {comport=}, {baudrate=}, {bind_port=}")
    prts = serial_ports_list()

    if n is not None:
        prt_device = prts[n].device
    elif comport is not None:
        prt_device = comport
    elif name is not None:
        prt_device = search_by_manufacturer(prts, name)
    else:
        raise ConnectionError("Port not defined")

    print(f"Opening: {prt_device} @ baudrate: {baudrate}")

    ard = PykiDev(prt_device, baudrate=baudrate)

    print("Testing ...")
    print(f"Arduino responded to hello with: {ard.hello()}")
    print(f"Set mode to: {ard.mode(1)}")

    if bind_port is None:
        return ard

    print("The ZeroRPC server is starting on:")
    print_my_ip()
    print(f":{bind_port}")

    server = zerorpc.Server(ard)
    server.bind(f"tcp://0.0.0.0:{bind_port}")
    print("The ZeroRPC server is running!")
    server.run()


if __name__ == "__main__":
    import fire
    fire.Fire(start_server)
