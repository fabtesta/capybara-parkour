# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Capybara Parkour is an arcade game featuring a capybara doing parkour, designed to run on a Raspberry Pi with a Nextion display connected via GPIO.

## Architecture

The project has three main components:

### 1. Display (`src/display/`)
Contains Nextion project files for the hardware display interface:
- `Cappi1.HMI` - Nextion Editor project file (editable source)
- `Cappi1.tft` - Compiled display firmware (upload to device)
- `0.zi` - Compressed assets/resources

### 2. Game Engine (`src/engine/`)
Python-based game engine with **Python-driven architecture** - all game logic runs in Python, Nextion acts as a rendering device.

**Core Modules:**
- `animation.py` - Animation and sprite system (`Animation`, `Sprite`, `AnimationManager`)
- `nextion.py` - Serial communication wrapper (`NextionDisplay`)
- `input.py` - Input event processing (`InputHandler`, `GameInput`)
- `game.py` - Main game loop base class (`Game`)
- `example_game.py` - Working example implementation

**Philosophy:** Python controls all timing, state machines, and logic. Nextion simply displays frames when told.

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

- **`asset-viewer.py`**: Graphical tool for previewing sprite sheets locally before deploying to hardware
  - Interactive sprite sheet viewer with animation playback
  - Supports custom grid dimensions and FPS control
  - Keyboard shortcuts: Space (play/pause), Left/Right arrows (navigate), R (reset)
  - Usage: `python asset-viewer.py <sprite_path> [--cols COLS] [--rows ROWS] [--fps FPS] [--scale SCALE]`
  - Example: `python asset-viewer.py ../../concept/capybara-sprite-walk.png --cols 4 --rows 3 --fps 10`

- **`split-sprite-sheet.py`**: Splits sprite sheets into individual frames for Nextion import
  - Converts grid-based sprite sheets to separate PNG files
  - Nextion requires individual images (no native sprite sheet support)
  - Usage: `python split-sprite-sheet.py <sprite_path> --cols COLS --rows ROWS [--output DIR] [--prefix PREFIX]`
  - Example: `python split-sprite-sheet.py ../../concept/capybara-sprite-walk.png --cols 4 --rows 3 --output ../../frames/walk`

## Nextion Serial Communication

All Nextion commands must end with three bytes: `\xff\xff\xff` (end-of-frame marker).

Serial connection parameters:
- Default port: `/dev/ttyAMA0` (Raspberry Pi GPIO UART)
- Baudrate: 9600 (standard), auto-detectable range: 2400-115200
- Parity: NONE
- Stop bits: 1
- Byte size: 8

## Dependencies

Core dependencies:
- `pyserial` - Serial communication with Nextion display
- `pillow` - Image processing for asset-viewer (optional, only for development)

Install dependencies:
```bash
pip install pyserial pillow
```

A Python virtual environment is set up in `src/scripts/venv/` for isolated development.

## Development Workflow

### Complete Animation Implementation Pipeline

**1. Preview sprite sheet locally:**
```bash
python src/scripts/asset-viewer.py concept/capybara-sprite-walk.png --cols 4 --rows 3 --fps 10
```

**2. Split sprite sheet into frames:**
```bash
python src/scripts/split-sprite-sheet.py concept/capybara-sprite-walk.png \
    --cols 4 --rows 3 --output frames/walk --prefix walk_
```

**3. Import frames into Nextion Editor:**
- Open `src/display/Cappi1.HMI`
- Picture → Import → Select all frames
- Note the picture IDs assigned (e.g., 0-11 for walk, 12-23 for run)

**4. Setup Nextion display components:**
- Add Picture component (name: `capybara`)
- Add Button components with Touch Release Events: `print "btn_name",0xff,0xff,0xff`

**5. Compile and upload to display:**
```bash
python src/scripts/rpi-interface.py src/display/Cappi1.tft /dev/ttyAMA0
```

**6. Run the game engine:**
```bash
cd src/engine
python example_game.py --port /dev/ttyAMA0
```

### Serial Communication Testing
- Monitor display output: `python src/scripts/read-nextion.py /dev/ttyAMA0`
- Send test commands: `python src/scripts/write-nextion.py`

### Running the Game
```bash
# Example game with capybara sprite
python src/engine/example_game.py --port /dev/ttyAMA0 --baudrate 9600

# Custom game implementation
python src/engine/game.py --port /dev/ttyAMA0
```

## Development Environment

- Target platform: Raspberry Pi
- Display: Nextion touchscreen (model format: NX####T### or NX####K###)
- Language: Python
- Hardware interface: GPIO serial connection

## Concept Assets

The `concept/` directory contains design assets:
- **Design Document**: `Capibara Parkour 2.pdf` - Game design reference
- **Sprite Sheets**:
  - `capybara-sprite-1.png`, `capybara-sprite-2.png` - Original sprite concepts
  - `capybara-sprite-walk.png` - Walking animation
  - `capybara-sprite-run.png` - Running animation
  - `capybara-sprite-jump.png` - Jumping animation
  - `capybara-hand-sprite-walk.png` - Hand-drawn walking variant

Use `asset-viewer.py` to preview and test these sprites before integrating into the Nextion display.

## Key Architecture Decisions

**Python-Driven Animation:**
- All animation timing, state machines, and game logic execute in Python
- Nextion display acts as a "dumb" rendering device
- Python sends picture IDs and positions via serial commands
- This maximizes flexibility and debugging capabilities

**Animation Frame Updates:**
- Python engine updates sprite frames based on elapsed time
- Only sends display updates when frames actually change (bandwidth optimization)
- Typical setup: 60 FPS game loop, 8-15 FPS sprite animations

**Serial Communication Pattern:**
- Commands: `component.property=value\xff\xff\xff`
- Example: `capybara.pic=5\xff\xff\xff` (update to frame 5)
- Input events: Nextion sends `print "event_name",0xff,0xff,0xff` on button press

See `src/engine/README.md` for detailed game engine documentation and examples.
