# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Capybara Parkour is an arcade game featuring a capybara doing parkour, designed to run on a Raspberry Pi with a Nextion display connected via GPIO.

## Architecture

The project has three main components:

### 1. Display (`src/display/`)
Contains Nextion project files for the hardware display interface. Currently empty - Nextion project files will be added here.

### 2. Game Engine (`src/engine/`)
Python-based game engine that:
- Reads from and writes to the Nextion display interface via serial communication
- Controls display pages, variables, and animations
- Implements the core game logic

Currently empty - game engine code will be developed here.

### 3. Utility Scripts (`src/scripts/`)
Python utilities for interfacing with the Nextion display:

- **`rpi-interface.py`**: Main upload utility for transferring compiled Nextion `.tft` files to the display
  - Auto-detects baudrate (2400-115200)
  - Verifies display model compatibility
  - Handles file transfer with progress display
  - Usage: `python rpi-interface.py <file.tft> <serial_port> [model_name]`

- **`write-nextion.py`**: Simple script demonstrating how to write text to Nextion display variables
  - Connects via `/dev/ttyAMA0` at 9600 baud
  - Shows basic command format: `page0.t0.txt="text"\xff\xff\xff`

- **`read-nextion.py`**: Script for reading data from the Nextion display
  - Continuously monitors serial input from the display
  - Usage: `python read-nextion.py <serial_port>`

## Nextion Serial Communication

All Nextion commands must end with three bytes: `\xff\xff\xff` (end-of-frame marker).

Serial connection parameters:
- Default port: `/dev/ttyAMA0` (Raspberry Pi GPIO UART)
- Baudrate: 9600 (standard), auto-detectable range: 2400-115200
- Parity: NONE
- Stop bits: 1
- Byte size: 8

## Dependencies

Requires `pyserial` library:
```bash
pip install pyserial
```
or
```bash
easy_install -U pyserial
```

## Development Environment

- Target platform: Raspberry Pi
- Display: Nextion touchscreen (model format: NX####T### or NX####K###)
- Language: Python
- Hardware interface: GPIO serial connection

## Concept Assets

The `concept/` directory contains design assets:
- PDF design document: `Capibara Parkour 2.pdf`
- Sprite sheets: `capybara-sprite-1.png`, `capybara-sprite-2.png`
