#!/usr/bin/env python3
"""
Example Game Implementation for Capybara Parkour

Demonstrates how to use the game engine to create a simple animated capybara game.

Setup Instructions:
1. Split your sprite sheets:
   python src/scripts/split-sprite-sheet.py concept/capybara-sprite-walk.png --cols 4 --rows 3 --output frames/walk --prefix walk_
   python src/scripts/split-sprite-sheet.py concept/capybara-sprite-run.png --cols 4 --rows 3 --output frames/run --prefix run_
   python src/scripts/split-sprite-sheet.py concept/capybara-sprite-jump.png --cols 4 --rows 3 --output frames/jump --prefix jump_

2. Import frames into Nextion Editor:
   - Open src/display/Cappi1.HMI
   - Go to Picture → Import
   - Import all frames in order (walk, run, jump)
   - Note the picture IDs assigned

3. Create Picture component in Nextion:
   - Add Picture component named "capybara"
   - Set initial pic to first frame ID
   - Position at (100, 150) or wherever you want

4. Add buttons in Nextion (optional):
   - Button "btn_walk" with Touch Release Event: print "btn_walk",0xff,0xff,0xff
   - Button "btn_run" with Touch Release Event: print "btn_run",0xff,0xff,0xff
   - Button "btn_jump" with Touch Release Event: print "btn_jump",0xff,0xff,0xff

5. Compile and upload to display:
   python src/scripts/rpi-interface.py src/display/Cappi1.tft /dev/ttyAMA0

6. Run this example:
   python src/engine/example_game.py --port /dev/ttyAMA0
"""

import sys
import time
from game import Game
from animation import Animation, Sprite


class CapybaraGame(Game):
    """Example Capybara Parkour game"""

    def __init__(self, port='/dev/ttyAMA0', baudrate=9600):
        super().__init__(port, baudrate, target_fps=60)

        # Game-specific state
        self.capybara_velocity_x = 0
        self.capybara_velocity_y = 0
        self.gravity = 500  # pixels per second^2
        self.jump_strength = -300  # pixels per second
        self.walk_speed = 50  # pixels per second
        self.run_speed = 100  # pixels per second
        self.is_jumping = False
        self.ground_y = 150  # Ground level

    def _create_sprites(self):
        """Create capybara sprite with animations"""
        # Create sprite
        capybara = Sprite("capybara", x=100, y=self.ground_y)

        # Define animations with picture IDs from Nextion
        # IMPORTANT: Update these IDs to match your actual Nextion picture resources!

        # Example mapping (adjust based on your import order):
        # Walk frames: IDs 0-11 (12 frames from 4x3 grid)
        walk_frame_ids = list(range(0, 12))

        # Run frames: IDs 12-23 (12 frames from 4x3 grid)
        run_frame_ids = list(range(12, 24))

        # Jump frames: IDs 24-35 (12 frames from 4x3 grid)
        jump_frame_ids = list(range(24, 36))

        # Create animations
        idle_anim = Animation("idle", frame_ids=[0], fps=1, loop=True)
        walk_anim = Animation("walk", frame_ids=walk_frame_ids, fps=10, loop=True)
        run_anim = Animation("run", frame_ids=run_frame_ids, fps=15, loop=True)
        jump_anim = Animation("jump", frame_ids=jump_frame_ids, fps=12, loop=False)

        # Add animations to sprite
        capybara.add_animation(idle_anim)
        capybara.add_animation(walk_anim)
        capybara.add_animation(run_anim)
        capybara.add_animation(jump_anim)

        # Start with idle
        capybara.play("idle")

        # Add to manager
        self.animation_manager.add_sprite(capybara)

        # Send initial state to display
        self.display.update_sprite("capybara",
                                   pic_id=capybara.get_current_frame_id(),
                                   x=capybara.x,
                                   y=capybara.y,
                                   visible=True)

        print("Capybara sprite created and initialized")

    def update(self, delta_time: float):
        """Update game logic"""
        # Get capybara sprite
        capybara = self.animation_manager.get_sprite("capybara")
        if not capybara:
            return

        # Store previous position
        prev_x = capybara.x
        prev_y = capybara.y

        # Handle input
        if self.game_input.is_just_pressed("jump") and not self.is_jumping:
            # Start jump
            self.capybara_velocity_y = self.jump_strength
            self.is_jumping = True
            capybara.play("jump")
            print("Jump!")

        elif self.game_input.is_pressed("run"):
            # Running
            self.capybara_velocity_x = self.run_speed
            if not self.is_jumping and capybara.current_animation.name != "run":
                capybara.play("run")

        elif self.game_input.is_pressed("walk"):
            # Walking
            self.capybara_velocity_x = self.walk_speed
            if not self.is_jumping and capybara.current_animation.name != "walk":
                capybara.play("walk")

        else:
            # Idle (no movement input)
            self.capybara_velocity_x = 0
            if not self.is_jumping and capybara.current_animation.name not in ["idle"]:
                capybara.play("idle")

        # Apply gravity
        if self.is_jumping:
            self.capybara_velocity_y += self.gravity * delta_time

        # Update position
        capybara.x += int(self.capybara_velocity_x * delta_time)
        capybara.y += int(self.capybara_velocity_y * delta_time)

        # Ground collision
        if capybara.y >= self.ground_y:
            capybara.y = self.ground_y
            self.capybara_velocity_y = 0
            if self.is_jumping:
                self.is_jumping = False
                # Return to appropriate animation
                if self.game_input.is_pressed("run"):
                    capybara.play("run")
                elif self.game_input.is_pressed("walk"):
                    capybara.play("walk")
                else:
                    capybara.play("idle")
                print("Landed!")

        # Screen boundaries (example: 480x320 display)
        capybara.x = max(0, min(capybara.x, 450))

        # Update animations
        frame_updates = self.animation_manager.update_all(delta_time)

        # Send updates to display
        # Update frame if changed
        for sprite_name, pic_id in frame_updates.items():
            self.display.set_picture(sprite_name, pic_id)

        # Update position if moved
        if prev_x != capybara.x or prev_y != capybara.y:
            self.display.set_position("capybara", capybara.x, capybara.y)

        # Clear frame input states
        self.game_input.update()

        # Debug output every 60 frames
        if self.frame_count % 60 == 0:
            print(f"FPS: {self.get_fps():.1f} | Pos: ({capybara.x}, {capybara.y}) | "
                  f"Anim: {capybara.current_animation.name if capybara.current_animation else 'None'}")


def main():
    """Run example game"""
    import argparse

    parser = argparse.ArgumentParser(description='Capybara Parkour Example Game')
    parser.add_argument('--port', type=str, default='/dev/ttyAMA0',
                       help='Serial port for Nextion display')
    parser.add_argument('--baudrate', type=int, default=9600,
                       help='Serial baudrate')

    args = parser.parse_args()

    print("=" * 60)
    print("Capybara Parkour - Example Game")
    print("=" * 60)
    print("\nControls (via Nextion buttons):")
    print("  - Walk button: Walk forward")
    print("  - Run button: Run forward")
    print("  - Jump button: Jump")
    print("\nPress Ctrl+C to exit\n")

    # Create and run game
    game = CapybaraGame(port=args.port, baudrate=args.baudrate)
    game.run()


if __name__ == '__main__':
    main()
