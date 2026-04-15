# SMILE – Scalable Modular Instrumentation for Laboratory Experiments

This repository contains a lightweight framework for building and controlling laboratory instrumentation using Arduino-based hardware and Python.

The project is designed to provide a simple and flexible alternative to large control frameworks, enabling a smooth transition from rapid prototyping to distributed experiment control.

---

## Project structure

The repository is organized into two main directories:

### 1. `pioArduinoProject`

Contains the firmware for the microcontroller.

- Built using PlatformIO
- Implements a command-based interface over serial communication
- Defines device parameters and measurement logic
- Designed for easy extension with new commands

---

### 2. `pythonHost`

Contains the Python-side control layer.

- Provides serial communication drivers (`Pykiba`, `PykiDev`)
- Enables automatic discovery of Arduino commands
- Supports both:
  - Centralized control (direct Python usage)
  - Distributed control (via ZeroRPC server)

---

## Core idea

The SMILE approach follows a natural workflow:

1. Build the hardware instrument using Arduino or compatible boards  
2. Implement control commands in the firmware  
3. Access and control the device from Python  
4. Optionally expose the device over the network using ZeroRPC  

This allows the same system to scale from a simple local script to a distributed laboratory setup without major architectural changes.

---

## How to use

### 1. Upload firmware

Navigate to the Arduino project:

```bash
cd pioArduinoProject
pio run --target upload
```

---

### 2. Use from Python (centralized mode)

```python
from pykidev import PykiDev

ard = PykiDev('/dev/ttyACM0', baudrate=9600)
print(ard.hello())
```

---

### 3. Run as a network service (distributed mode)

```bash
smile --n=0 --baudrate=9600 --bind_port=2020
```

Multiple clients can then connect to the same device.

---

## Platform notes

The firmware has been tested on:

- Arduino Mega 2560 (ATmega2560)  
- NUCLEO-L010RB (STM32L010RB)

**Linux:**  
Both platforms operate reliably across the full baud rate range from **9600 to 115200**.

**Windows:**  
The Arduino Mega 2560 board used in this project was observed to work reliably only at **9600 and approximately 57600 baud**.  
Higher baud rates may result in unstable or corrupted serial communication.

---

## Requirements

- PlatformIO (for firmware build and upload)  
- Python ≥ 3.8  
- Required Python packages (see `pythonHost/pyproject.toml` or `requirements.txt`)  

---

## License (Beerware)

"THE BEER-WARE LICENSE" (Revision 42):

As long as you retain this notice, you can do whatever you want with this stuff.  
If we meet someday, and you think this stuff is worth it, you can buy me a beer in return.

— Kamen Kamenov

---

## Notes

This project is intended for small-scale experimental systems where simplicity, transparency, and rapid development are more important than heavy infrastructure.
