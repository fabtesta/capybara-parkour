"""
Nextion Display Communication Module

Handles serial communication with Nextion displays.
Provides high-level interface for updating sprites, reading input, and controlling display.
"""

import serial
import time
from typing import Optional, Tuple, List
import threading


class NextionDisplay:
    """Handles serial communication with Nextion display"""

    # Nextion command terminator
    CMD_END = b"\xff\xff\xff"

    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 9600, timeout: float = 0.1):
        """
        Initialize connection to Nextion display.

        Args:
            port: Serial port (e.g., '/dev/ttyAMA0' on Raspberry Pi, 'COM3' on Windows)
            baudrate: Communication speed (default 9600)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """
        Establish connection to Nextion display.

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            time.sleep(0.1)  # Allow display to initialize
            self.connected = True
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Nextion: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Close connection to Nextion display"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False

    def send_command(self, command: str) -> bool:
        """
        Send a command to Nextion display.

        Args:
            command: Command string (without terminator)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected or not self.ser:
            return False

        try:
            with self._lock:
                full_command = command.encode() + self.CMD_END
                self.ser.write(full_command)
                print(f"Sent command: {command}")
                return True
        except serial.SerialException as e:
            print(f"Error sending command: {e}")
            return False

    def set_picture(self, component_name: str, pic_id: int) -> bool:
        """
        Update picture component to display a specific frame.

        Args:
            component_name: Name of Picture component in Nextion (e.g., "capybara")
            pic_id: Nextion picture resource ID

        Returns:
            True if command sent successfully
        """
        command = f"{component_name}.pic={pic_id}"
        return self.send_command(command)

    def set_position(self, component_name: str, x: int, y: int) -> bool:
        """
        Move a component to a new position.

        Args:
            component_name: Name of component in Nextion
            x: X coordinate
            y: Y coordinate

        Returns:
            True if commands sent successfully
        """
        success = True
        success &= self.send_command(f"{component_name}.x={x}")
        success &= self.send_command(f"{component_name}.y={y}")
        return success

    def set_visibility(self, component_name: str, visible: bool) -> bool:
        """
        Show or hide a component.

        Args:
            component_name: Name of component in Nextion
            visible: True to show, False to hide

        Returns:
            True if command sent successfully
        """
        vis_value = 1 if visible else 0
        return self.send_command(f"{component_name}.vis={vis_value}")

    def set_text(self, component_name: str, text: str) -> bool:
        """
        Update text component content.

        Args:
            component_name: Name of Text component in Nextion
            text: Text content to display

        Returns:
            True if command sent successfully
        """
        # Escape quotes in text
        escaped_text = text.replace('"', '\\"')
        command = f'{component_name}.txt="{escaped_text}"'
        return self.send_command(command)

    def set_value(self, component_name: str, value: int) -> bool:
        """
        Update numeric value of a component.

        Args:
            component_name: Name of component in Nextion
            value: Numeric value

        Returns:
            True if command sent successfully
        """
        command = f"{component_name}.val={value}"
        return self.send_command(command)

    def change_page(self, page_id: int) -> bool:
        """
        Switch to a different page.

        Args:
            page_id: Page number (0-indexed)

        Returns:
            True if command sent successfully
        """
        command = f"page {page_id}"
        return self.send_command(command)

    def read_data(self, max_bytes: int = 128) -> bytes:
        """
        Read available data from Nextion display.

        Args:
            max_bytes: Maximum bytes to read

        Returns:
            Bytes read from display
        """
        if not self.connected or not self.ser:
            return b""

        try:
            with self._lock:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(min(self.ser.in_waiting, max_bytes))
                    print(f"Received data: {data}")
                    return data
        except serial.SerialException as e:
            print(f"Error reading data: {e}")

        return b""

    def read_until_terminator(self, timeout: Optional[float] = None) -> bytes:
        """
        Read data until Nextion terminator is received.

        Args:
            timeout: Read timeout in seconds (uses default if None)

        Returns:
            Complete message including terminator
        """
        if not self.connected or not self.ser:
            return b""

        try:
            with self._lock:
                old_timeout = self.ser.timeout
                if timeout is not None:
                    self.ser.timeout = timeout
                data = self.ser.read_until(self.CMD_END)
                self.ser.timeout = old_timeout
                print(f"Received data: {data}")
                return data
        except serial.SerialException as e:
            print(f"Error reading data: {e}")
            return b""

    def update_sprite(self, sprite_name: str, pic_id: Optional[int] = None,
                     x: Optional[int] = None, y: Optional[int] = None,
                     visible: Optional[bool] = None) -> bool:
        """
        Update multiple sprite properties at once (optimized).

        Args:
            sprite_name: Name of sprite component
            pic_id: Picture ID (if changing frame)
            x: X position (if moving)
            y: Y position (if moving)
            visible: Visibility state (if changing)

        Returns:
            True if all commands sent successfully
        """
        success = True

        if pic_id is not None:
            success &= self.set_picture(sprite_name, pic_id)

        if x is not None and y is not None:
            success &= self.set_position(sprite_name, x, y)
        elif x is not None:
            success &= self.send_command(f"{sprite_name}.x={x}")
        elif y is not None:
            success &= self.send_command(f"{sprite_name}.y={y}")

        if visible is not None:
            success &= self.set_visibility(sprite_name, visible)

        return success

    def clear_buffer(self):
        """Clear any pending data in the serial buffer"""
        if self.connected and self.ser:
            with self._lock:
                self.ser.reset_input_buffer()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def __repr__(self):
        status = "connected" if self.connected else "disconnected"
        return f"NextionDisplay(port={self.port}, baudrate={self.baudrate}, status={status})"
