# DFRobot 8-Channel USB Relay Control (Python GUI)

This project provides a Tkinter-based GUI application to control a DFRobot 8-Channel USB Relay module over a serial (USB) connection.  
It supports individual relay control, status indicators, relay descriptions, and persistent state storage.

---

## Features

- Control 8 relays individually (ON / OFF)
- ALL ON / ALL OFF buttons
- Visual status indicator  
  - Green = ON  
  - Red = OFF
- Editable description field per relay
- Save & load:
  - Relay descriptions (`relay_descriptions.txt`)
  - Relay ON/OFF states (`relay_states.txt`)
- Automatic relay USB serial port detection
- Windows EXE build support using PyInstaller

---

## Requirements

### Software
- Windows
- Python 3.9 or newer
- Python packages:

### Hardware
- DFRobot 8-Channel USB Relay
- USB connection to the PC

---

## Running the Application


On startup, the application:
- Detects the relay USB serial port
- Restores previous relay states
- Loads saved relay descriptions (if available)

---

## Relay Controls

Each relay row contains:
- Relay number label
- ON / OFF toggle button
- Status indicator (circle)
- Description input field
- Save and Clear buttons

---

## Persistent Files

| File Name | Description |
|----------|-------------|
| relay_descriptions.txt | Stores relay descriptions |
| relay_states.txt | Stores relay ON/OFF states |

These files are created automatically in the same directory as the script or executable.

---

## Building a Windows Executable

Use PyInstaller to generate a standalone EXE:


The executable will be created in:


---

## Notes & Troubleshooting

- Ensure the relay is connected before launching the application
- The relay must appear as **USB Serial Device** in Windows Device Manager
- Baud rate used: **115200**
- Only one relay device is expected to be connected at a time

---

## Recommended Project Structure


---

## License

This project is provided as-is for educational and internal tooling purposes.
