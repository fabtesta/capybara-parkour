"""
Input Handler for Capybara Parkour

Processes input events from Nextion display (button presses, touch events, etc.)
"""

from typing import Callable, Dict, Optional
from enum import Enum


class InputEvent(Enum):
    """Types of input events from Nextion"""
    BUTTON_PRESS = "button"
    TOUCH_PRESS = "touch_press"
    TOUCH_RELEASE = "touch_release"
    SLIDER_CHANGE = "slider"
    CUSTOM = "custom"


class InputHandler:
    """Handles input events from Nextion display"""

    def __init__(self):
        """Initialize input handler"""
        self.callbacks: Dict[str, Callable] = {}
        self.buffer = b""

    def register_callback(self, event_name: str, callback: Callable):
        """
        Register a callback function for a specific event.

        Args:
            event_name: Name of the event to listen for (e.g., "btn_jump", "touch_area")
            callback: Function to call when event occurs
        """
        self.callbacks[event_name] = callback

    def unregister_callback(self, event_name: str):
        """Remove a callback for an event"""
        if event_name in self.callbacks:
            del self.callbacks[event_name]

    def process_data(self, data: bytes):
        """
        Process incoming data from Nextion.

        Args:
            data: Raw bytes from serial connection
        """
        if not data:
            return

        # Add to buffer
        self.buffer += data

        # Process complete messages (terminated with \xff\xff\xff)
        while b"\xff\xff\xff" in self.buffer:
            # Find terminator
            term_index = self.buffer.find(b"\xff\xff\xff")
            message = self.buffer[:term_index]
            self.buffer = self.buffer[term_index + 3:]

            # Process the message
            self._handle_message(message)

    def _handle_message(self, message: bytes):
        """
        Handle a complete message from Nextion.

        Args:
            message: Complete message without terminator
        """
        if not message:
            return

        try:
            # Try to decode as text (for custom print commands)
            msg_str = message.decode('latin1').strip()

            # Check if any registered callbacks match
            for event_name, callback in self.callbacks.items():
                if event_name in msg_str:
                    callback(msg_str)
                    return

        except Exception as e:
            print(f"Error processing input: {e}")

    def clear_buffer(self):
        """Clear the input buffer"""
        self.buffer = b""


class GameInput:
    """High-level game input manager"""

    def __init__(self):
        """Initialize game input manager"""
        self.button_states: Dict[str, bool] = {}
        self.just_pressed: Dict[str, bool] = {}
        self.just_released: Dict[str, bool] = {}

    def update(self):
        """
        Update input state (call once per frame).
        Clears just_pressed and just_released states.
        """
        self.just_pressed.clear()
        self.just_released.clear()

    def press_button(self, button_name: str):
        """
        Register a button press.

        Args:
            button_name: Name of the button
        """
        if not self.button_states.get(button_name, False):
            self.button_states[button_name] = True
            self.just_pressed[button_name] = True

    def release_button(self, button_name: str):
        """
        Register a button release.

        Args:
            button_name: Name of the button
        """
        if self.button_states.get(button_name, False):
            self.button_states[button_name] = False
            self.just_released[button_name] = True

    def is_pressed(self, button_name: str) -> bool:
        """
        Check if a button is currently pressed.

        Args:
            button_name: Name of the button

        Returns:
            True if button is pressed, False otherwise
        """
        return self.button_states.get(button_name, False)

    def is_just_pressed(self, button_name: str) -> bool:
        """
        Check if a button was just pressed this frame.

        Args:
            button_name: Name of the button

        Returns:
            True if button was just pressed
        """
        return self.just_pressed.get(button_name, False)

    def is_just_released(self, button_name: str) -> bool:
        """
        Check if a button was just released this frame.

        Args:
            button_name: Name of the button

        Returns:
            True if button was just released
        """
        return self.just_released.get(button_name, False)

    def reset(self):
        """Reset all input states"""
        self.button_states.clear()
        self.just_pressed.clear()
        self.just_released.clear()
