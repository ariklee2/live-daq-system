# live-daq-system

## Overview

This project is a **real-time data acquisition (DAQ) and visualization system** built using a **LabJack T7**, **Python**, and **PyQt5**. It continuously streams **pressure** and **temperature** data from analog input channels, converts raw voltages into physical units, plots the results live, and logs all measurements to a CSV file for post-processing.

The system was intended for **sensor calibration, verification, and live monitoring**.

---

## Features

- **Real-time streaming** from LabJack analog inputs using `ljm.eStream`
- **Live plotting** of temperature and pressure using PyQtGraph
- **Voltage-to-unit conversion**
  - Pressure: voltage → PSI
  - Temperature: thermocouple voltage → °F
- **CSV data logging** with timestamps
- **Start / Stop controls** for safe data acquisition
- **Sliding time window** for smooth, responsive plots

---

## Hardware Configuration

| Sensor | LabJack Channel | Notes |
|------|----------------|-------|
| Pressure Transducer | `AIN0` | 0.5–4.5 V output |
| Thermocouple (Differential) | `AIN2` (+), `AIN3` (−) | Differential measurement |

Thermocouple voltage is measured in **millivolts**, referenced against a lookup table, and linearly interpolated to compute temperature.

---

## Software Stack

- **Python 3**
- **LabJack LJM Library**
- **PyQt5** – GUI framework
- **PyQtGraph** – Real-time plotting
- **CSV** – Data logging
- **Datetime** – Timestamp generation

---

## How It Works

### Start Streaming
- Opens a LabJack device connection
- Initializes analog streaming at **1000 Hz**
- Configures differential mode for the thermocouple
- Creates a CSV file (`ain_log.csv`)
- Starts a GUI update timer at 100 ms intervals

### Data Acquisition Loop
- Reads raw voltages from the LabJack stream
- Converts voltages into engineering units
- Updates GUI labels with live values
- Appends data to scrolling plots
- Logs timestamped data to CSV

### Stop Streaming
- Stops the LabJack stream
- Closes the device handle
- Flushes and closes the CSV file

---

## Conversion Methods

### Pressure Conversion

```python
def voltage_to_psi(voltage):
    return ((voltage - 0.5) / (4.5 - 0.5)) * 1600
```

### Temperature Conversion

```python
def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32
```

## Output Data Format
All data is logged to ain_log.csv with the following structure:

| Column | Description |
|--------|-------------|
| Timestamp | Local system time |
| AIN0 (V) | Raw pressure sensor voltage |
| Pressure (PSI) | Converted pressure value |
| AIN2 (V) | Raw thermocouple voltage |
| Temperature (°F) | Converted temperature value |
