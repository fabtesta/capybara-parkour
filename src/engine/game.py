"""
Main Game Loop for Capybara Parkour

Integrates animation system, Nextion display, and input handling.
"""

import time
import sys
from typing import Optional

from animation import Animation, Sprite, AnimationManager
from nextion import NextionDisplay
from input import InputHandler, GameInput


class Game:
    """Main game class"""

    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 9600, target_fps: int = 60):
        """
        Initialize game.

        Args:
            port: Serial port for Nextion display
            baudrate: Serial communication speed
            target_fps: Target frames per second for game loop
        """
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False

        # Initialize display
        self.display = NextionDisplay(port, baudrate)

        # Initialize animation manager
        self.animation_manager = AnimationManager()

        # Initialize input handling
        self.input_handler = InputHandler()
        self.game_input = GameInput()

        # Setup input callbacks
        self._setup_input_callbacks()

        # Game state
        self.frame_count = 0
        self.elapsed_time = 0.0

    def _setup_input_callbacks(self):
        """Setup callbacks for input events from Nextion"""
        # Register callbacks for button events
        # These should match the print commands in your Nextion project

        # Example: Button sends "btn_jump" when pressed
        self.input_handler.register_callback("btn_jump",
                                            lambda msg: self.game_input.press_button("jump"))

        # Example: Button sends "btn_walk" when pressed
        self.input_handler.register_callback("btn_walk",
                                            lambda msg: self.game_input.press_button("walk"))

        # Example: Button sends "btn_run" when pressed
        self.input_handler.register_callback("btn_run",
                                            lambda msg: self.game_input.press_button("run"))

    def initialize(self) -> bool:
        """
        Initialize game systems.

        Returns:
            True if initialization successful
        """
        print("Initializing Capybara Parkour...")

        # Connect to display
        if not self.display.connect():
            print("Failed to connect to Nextion display")
            return False

        print(f"Connected to Nextion display on {self.display.port}")

        # Initialize game objects
        self._create_sprites()

        print("Game initialized successfully")
        return True

    def _create_sprites(self):
        """
        Create and configure game sprites.
        Override this method to setup your specific sprites and animations.
        """
        # Example: Create capybara sprite
        capybara = Sprite("capybara", x=100, y=150)

        # Define animations
        # NOTE: Update these frame IDs to match your Nextion picture resource IDs
        idle_anim = Animation("idle", frame_ids=[0], fps=1, loop=True)
        walk_anim = Animation("walk", frame_ids=[0, 1, 2, 3], fps=10, loop=True)
        run_anim = Animation("run", frame_ids=[4, 5, 6, 7, 8, 9], fps=15, loop=True)
        jump_anim = Animation("jump", frame_ids=[10, 11, 12, 13, 14], fps=12, loop=False)

        # Add animations to sprite
        capybara.add_animation(idle_anim)
        capybara.add_animation(walk_anim)
        capybara.add_animation(run_anim)
        capybara.add_animation(jump_anim)

        # Start with idle animation
        capybara.play("idle")

        # Add to animation manager
        self.animation_manager.add_sprite(capybara)

        # Send initial state to display
        self.display.update_sprite("capybara",
                                   pic_id=capybara.get_current_frame_id(),
                                   x=capybara.x,
                                   y=capybara.y)

    def update(self, delta_time: float):
        """
        Update game logic.
        Override this method to implement your game logic.

        Args:
            delta_time: Time elapsed since last frame
        """
        # Update animations
        frame_updates = self.animation_manager.update_all(delta_time)

        # Send frame updates to display
        for sprite_name, pic_id in frame_updates.items():
            self.display.set_picture(sprite_name, pic_id)

        # Example game logic
        capybara = self.animation_manager.get_sprite("capybara")
        if capybara:
            # Handle jump button
            if self.game_input.is_just_pressed("jump"):
                capybara.play("jump")

            # Handle walk button
            elif self.game_input.is_just_pressed("walk"):
                capybara.play("walk")

            # Handle run button
            elif self.game_input.is_just_pressed("run"):
                capybara.play("run")

            # Return to idle after non-looping animation
            if capybara.is_animation_finished():
                capybara.play("idle")

        # Clear frame input states
        self.game_input.update()

    def handle_input(self):
        """Process input from Nextion display"""
        # Read any available data
        data = self.display.read_data()
        if data:
            self.input_handler.process_data(data)

    def run(self):
        """Main game loop"""
        if not self.initialize():
            print("Failed to initialize game")
            return

        self.running = True
        last_time = time.time()

        print(f"Starting game loop (target: {self.target_fps} FPS)")
        print("Press Ctrl+C to exit")

        try:
            while self.running:
                # Calculate delta time
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                # Process input
                self.handle_input()

                # Update game
                self.update(delta_time)

                # Update counters
                self.frame_count += 1
                self.elapsed_time += delta_time

                # Sleep to maintain target FPS
                sleep_time = self.frame_time - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.shutdown()

    def shutdown(self):
        """Cleanup and shutdown game"""
        print("Cleaning up...")
        self.running = False
        self.display.disconnect()
        print(f"Game ran for {self.elapsed_time:.2f} seconds ({self.frame_count} frames)")
        print("Goodbye!")

    def get_fps(self) -> float:
        """
        Calculate actual FPS.

        Returns:
            Current frames per second
        """
        if self.elapsed_time > 0:
            return self.frame_count / self.elapsed_time
        return 0.0


def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Capybara Parkour Game')
    parser.add_argument('--port', type=str, default='/dev/ttyAMA0',
                       help='Serial port for Nextion display (default: /dev/ttyAMA0)')
    parser.add_argument('--baudrate', type=int, default=9600,
                       help='Serial baudrate (default: 9600)')
    parser.add_argument('--fps', type=int, default=60,
                       help='Target frames per second (default: 60)')

    args = parser.parse_args()

    # Create and run game
    game = Game(port=args.port, baudrate=args.baudrate, target_fps=args.fps)
    game.run()


if __name__ == '__main__':
    main()
