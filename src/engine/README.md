# Capybara Parkour Game Engine

Python-based game engine for Raspberry Pi with Nextion display integration.

## Architecture

The engine follows a **Python-driven architecture** where all game logic, animation timing, and state management happens in Python, while the Nextion display acts as a "dumb" rendering device.

### Components

- **`animation.py`** - Animation and sprite management
  - `Animation` - Defines frame sequences and timing
  - `Sprite` - Manages sprite state and animation playback
  - `AnimationManager` - Orchestrates multiple sprites

- **`nextion.py`** - Serial communication with Nextion display
  - `NextionDisplay` - Low-level display control
  - Handles sending commands and reading input

- **`input.py`** - Input event processing
  - `InputHandler` - Processes raw input from Nextion
  - `GameInput` - High-level button state tracking

- **`game.py`** - Main game loop
  - `Game` - Base game class with update loop
  - Ties all systems together

## Quick Start

### 1. Prepare Sprite Sheets

Split your sprite sheets into individual frames:

```bash
# Walk animation
python src/scripts/split-sprite-sheet.py concept/capybara-sprite-walk.png \
    --cols 4 --rows 3 --output frames/walk --prefix walk_

# Run animation
python src/scripts/split-sprite-sheet.py concept/capybara-sprite-run.png \
    --cols 4 --rows 3 --output frames/run --prefix run_

# Jump animation
python src/scripts/split-sprite-sheet.py concept/capybara-sprite-jump.png \
    --cols 4 --rows 3 --output frames/jump --prefix jump_
```

### 2. Setup Nextion Display

In Nextion Editor (`src/display/Cappi1.HMI`):

1. **Import frames**:
   - Go to Picture → Import
   - Import all frames in order
   - Note the picture IDs assigned (e.g., 0-11 for walk, 12-23 for run, etc.)

2. **Add Picture component**:
   - Drag Picture component onto your page
   - Name: `capybara`
   - Set initial `pic` to first frame ID
   - Position: (100, 150) or wherever you want

3. **Add control buttons** (optional):
   - Add Button components: `btn_walk`, `btn_run`, `btn_jump`
   - Set Touch Release Events:
     - `btn_walk`: `print "btn_walk",0xff,0xff,0xff`
     - `btn_run`: `print "btn_run",0xff,0xff,0xff`
     - `btn_jump`: `print "btn_jump",0xff,0xff,0xff`

4. **Compile and upload**:
   ```bash
   python src/scripts/rpi-interface.py src/display/Cappi1.tft /dev/ttyAMA0
   ```

### 3. Run Example Game

```bash
cd src/engine
python example_game.py --port /dev/ttyAMA0
```

## Usage

### Basic Game Structure

```python
from game import Game
from animation import Animation, Sprite

class MyGame(Game):
    def _create_sprites(self):
        """Setup sprites and animations"""
        # Create sprite
        player = Sprite("player", x=100, y=100)

        # Define animations with Nextion picture IDs
        walk = Animation("walk", frame_ids=[0, 1, 2, 3], fps=10, loop=True)
        jump = Animation("jump", frame_ids=[4, 5, 6], fps=12, loop=False)

        # Add to sprite
        player.add_animation(walk)
        player.add_animation(jump)
        player.play("walk")

        # Add to manager
        self.animation_manager.add_sprite(player)

    def update(self, delta_time):
        """Game logic"""
        player = self.animation_manager.get_sprite("player")

        # Handle input
        if self.game_input.is_just_pressed("jump"):
            player.play("jump")

        # Update animations
        frame_updates = self.animation_manager.update_all(delta_time)

        # Send to display
        for name, pic_id in frame_updates.items():
            self.display.set_picture(name, pic_id)

        self.game_input.update()

# Run game
game = MyGame(port='/dev/ttyAMA0')
game.run()
```

### Animation System

```python
# Create animation
walk = Animation(
    name="walk",
    frame_ids=[0, 1, 2, 3],  # Nextion picture IDs
    fps=10,                   # Frames per second
    loop=True                 # Loop when finished
)

# Create sprite
sprite = Sprite("player", x=100, y=100)
sprite.add_animation(walk)

# Control playback
sprite.play("walk")          # Start animation
sprite.pause()               # Pause
sprite.resume()              # Resume
sprite.stop()                # Stop

# Update (call every frame)
delta_time = 0.016  # ~60 FPS
new_frame = sprite.update(delta_time)
if new_frame is not None:
    # Frame changed, update display
    display.set_picture("player", new_frame)
```

### Display Communication

```python
display = NextionDisplay('/dev/ttyAMA0', baudrate=9600)
display.connect()

# Update sprite frame
display.set_picture("capybara", pic_id=5)

# Move sprite
display.set_position("capybara", x=150, y=100)

# Update multiple properties
display.update_sprite("capybara", pic_id=5, x=150, y=100, visible=True)

# Update text
display.set_text("score_label", "Score: 1000")

# Change page
display.change_page(1)
```

### Input Handling

```python
# Register callbacks
input_handler = InputHandler()
input_handler.register_callback("btn_jump", lambda msg: print("Jump!"))

# Process incoming data
data = display.read_data()
input_handler.process_data(data)

# High-level input tracking
game_input = GameInput()

# In input callback
game_input.press_button("jump")

# In game loop
if game_input.is_just_pressed("jump"):
    # Jump logic
    pass

game_input.update()  # Clear frame states
```

## Performance Tips

1. **Only send updates when needed**:
   - Check if frame actually changed before sending
   - Only update position when sprite moves

2. **Batch operations**:
   - Use `update_sprite()` to send multiple properties at once

3. **Target FPS**:
   - 60 FPS game loop recommended
   - Animation FPS can be lower (8-15 FPS typical)

4. **Serial bandwidth**:
   - Each command is ~20 bytes
   - At 9600 baud: ~480 commands/second max
   - 60 FPS = 16ms per frame, plenty of time for updates

## Troubleshooting

### Display not responding
- Check serial connection: `ls /dev/tty*`
- Verify baudrate matches Nextion project
- Try `python src/scripts/read-nextion.py /dev/ttyAMA0` to test connection

### Animations not playing
- Verify picture IDs match your Nextion resources
- Check frame_ids list in Animation definition
- Add debug prints in `update()` to see frame changes

### Input not working
- Verify Nextion buttons have correct `print` commands
- Check callback registration matches event names
- Test with `python src/scripts/read-nextion.py` to see raw input

### Low FPS
- Reduce animation update frequency
- Only send updates when values change
- Increase baudrate if possible (19200, 38400)

## Next Steps

- Implement collision detection
- Add physics system
- Create level management
- Implement scoring system
- Add sound effects (if Nextion supports)
- Create multiple game states (menu, playing, game over)
