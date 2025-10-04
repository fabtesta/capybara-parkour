#!/usr/bin/env python3
"""
Graphical Asset Viewer for Capybara Parkour

A utility to preview and test sprite sheets and animations locally
before deploying to the Nextion display.

Usage:
    python asset-viewer.py <sprite_sheet_path> [--cols COLS] [--rows ROWS] [--fps FPS]

Examples:
    python asset-viewer.py ../../concept/capybara-sprite-1.png --cols 4 --rows 3
    python asset-viewer.py ../../concept/capybara-sprite-2.png --cols 4 --rows 3 --fps 8
"""

import os
import sys
import argparse
from typing import List, Tuple

try:
    from PIL import Image, ImageTk
    import tkinter as tk
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install dependencies:")
    print("  pip install pillow")
    sys.exit(1)


class SpriteSheet:
    """Handles loading and slicing sprite sheets into individual frames"""

    def __init__(self, filepath: str, cols: int = 4, rows: int = 3):
        """
        Initialize sprite sheet

        Args:
            filepath: Path to the sprite sheet image
            cols: Number of columns in the sprite grid
            rows: Number of rows in the sprite grid
        """
        self.filepath = filepath
        self.cols = cols
        self.rows = rows
        self.image = Image.open(filepath)
        self.frames = self._extract_frames()

    def _extract_frames(self) -> List[Image.Image]:
        """Extract individual sprite frames from the sheet"""
        width, height = self.image.size
        frame_width = width // self.cols
        frame_height = height // self.rows

        frames = []
        for row in range(self.rows):
            for col in range(self.cols):
                left = col * frame_width
                top = row * frame_height
                right = left + frame_width
                bottom = top + frame_height

                frame = self.image.crop((left, top, right, bottom))
                frames.append(frame)

        return frames

    def get_frame(self, index: int) -> Image.Image:
        """Get a specific frame by index"""
        return self.frames[index % len(self.frames)]

    def get_frame_count(self) -> int:
        """Get total number of frames"""
        return len(self.frames)


class AssetViewer:
    """Interactive viewer for sprite sheets with animation playback"""

    def __init__(self, sprite_sheet: SpriteSheet, fps: int = 10, scale: int = 3):
        """
        Initialize the viewer

        Args:
            sprite_sheet: SpriteSheet object to display
            fps: Frames per second for animation
            scale: Scaling factor for display
        """
        self.sprite_sheet = sprite_sheet
        self.fps = fps
        self.scale = scale
        self.current_frame = 0
        self.is_playing = False

        # Setup window
        self.root = tk.Tk()
        self.root.title(f"Asset Viewer - {os.path.basename(sprite_sheet.filepath)}")

        # Create UI
        self._create_ui()

        # Animation timer
        self.frame_delay = int(1000 / fps)  # milliseconds
        self.after_id = None

    def _create_ui(self):
        """Create the user interface"""
        # Main frame for sprite display
        self.canvas_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.canvas_frame.pack(padx=10, pady=10)

        # Canvas for displaying sprite
        frame = self.sprite_sheet.get_frame(0)
        canvas_width = frame.width * self.scale
        canvas_height = frame.height * self.scale

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=canvas_width,
            height=canvas_height,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.canvas.pack()

        # Info label
        info_text = (
            f"Sprite Sheet: {os.path.basename(self.sprite_sheet.filepath)} | "
            f"Grid: {self.sprite_sheet.cols}x{self.sprite_sheet.rows} | "
            f"Total Frames: {self.sprite_sheet.get_frame_count()} | "
            f"FPS: {self.fps}"
        )
        self.info_label = tk.Label(self.root, text=info_text, font=('Arial', 9))
        self.info_label.pack(pady=(0, 5))

        # Frame counter
        self.frame_label = tk.Label(
            self.root,
            text=f"Frame: {self.current_frame + 1}/{self.sprite_sheet.get_frame_count()}",
            font=('Arial', 10, 'bold')
        )
        self.frame_label.pack(pady=5)

        # Controls frame
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=5)

        # Control buttons
        self.play_button = tk.Button(
            controls_frame,
            text="▶ Play",
            command=self.toggle_play,
            width=10
        )
        self.play_button.grid(row=0, column=0, padx=5)

        tk.Button(
            controls_frame,
            text="◀ Prev",
            command=self.prev_frame,
            width=10
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            controls_frame,
            text="Next ▶",
            command=self.next_frame,
            width=10
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            controls_frame,
            text="⟲ Reset",
            command=self.reset,
            width=10
        ).grid(row=0, column=3, padx=5)

        # FPS control
        fps_frame = tk.Frame(self.root)
        fps_frame.pack(pady=5)

        tk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT, padx=5)

        self.fps_scale = tk.Scale(
            fps_frame,
            from_=1,
            to=30,
            orient=tk.HORIZONTAL,
            command=self.update_fps,
            length=200
        )
        self.fps_scale.set(self.fps)
        self.fps_scale.pack(side=tk.LEFT)

        # Keyboard bindings
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Left>', lambda e: self.prev_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())
        self.root.bind('<r>', lambda e: self.reset())

        # Initial display
        self.display_frame()

    def display_frame(self):
        """Display the current frame on the canvas"""
        frame = self.sprite_sheet.get_frame(self.current_frame)

        # Scale the frame
        scaled_width = frame.width * self.scale
        scaled_height = frame.height * self.scale
        scaled_frame = frame.resize((scaled_width, scaled_height), Image.NEAREST)

        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(scaled_frame)

        # Clear and draw
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Update frame label
        self.frame_label.config(
            text=f"Frame: {self.current_frame + 1}/{self.sprite_sheet.get_frame_count()}"
        )

    def next_frame(self):
        """Advance to next frame"""
        self.current_frame = (self.current_frame + 1) % self.sprite_sheet.get_frame_count()
        self.display_frame()

    def prev_frame(self):
        """Go to previous frame"""
        self.current_frame = (self.current_frame - 1) % self.sprite_sheet.get_frame_count()
        self.display_frame()

    def reset(self):
        """Reset to first frame"""
        self.current_frame = 0
        self.display_frame()

    def toggle_play(self):
        """Toggle animation playback"""
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_button.config(text="⏸ Pause")
            self.animate()
        else:
            self.play_button.config(text="▶ Play")
            if self.after_id:
                self.root.after_cancel(self.after_id)

    def animate(self):
        """Animation loop"""
        if self.is_playing:
            self.next_frame()
            self.after_id = self.root.after(self.frame_delay, self.animate)

    def update_fps(self, value):
        """Update FPS from slider"""
        self.fps = int(value)
        self.frame_delay = int(1000 / self.fps)
        self.info_label.config(
            text=(
                f"Sprite Sheet: {os.path.basename(self.sprite_sheet.filepath)} | "
                f"Grid: {self.sprite_sheet.cols}x{self.sprite_sheet.rows} | "
                f"Total Frames: {self.sprite_sheet.get_frame_count()} | "
                f"FPS: {self.fps}"
            )
        )

    def run(self):
        """Start the viewer"""
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(
        description='View and test sprite sheet animations for Capybara Parkour'
    )
    parser.add_argument(
        'sprite_path',
        help='Path to sprite sheet image file'
    )
    parser.add_argument(
        '--cols',
        type=int,
        default=4,
        help='Number of columns in sprite grid (default: 4)'
    )
    parser.add_argument(
        '--rows',
        type=int,
        default=3,
        help='Number of rows in sprite grid (default: 3)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=10,
        help='Animation frames per second (default: 10)'
    )
    parser.add_argument(
        '--scale',
        type=int,
        default=3,
        help='Display scaling factor (default: 3)'
    )

    args = parser.parse_args()

    # Validate file
    if not os.path.isfile(args.sprite_path):
        print(f"Error: File not found: {args.sprite_path}")
        sys.exit(1)

    try:
        # Load sprite sheet
        sprite_sheet = SpriteSheet(args.sprite_path, args.cols, args.rows)

        # Create and run viewer
        viewer = AssetViewer(sprite_sheet, args.fps, args.scale)
        viewer.run()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
