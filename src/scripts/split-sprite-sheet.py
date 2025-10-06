#!/usr/bin/env python3
"""
Sprite Sheet Splitter for Capybara Parkour

Splits a sprite sheet into individual frame images for import into Nextion Editor.

Usage:
    python split-sprite-sheet.py <sprite_sheet_path> --cols COLS --rows ROWS [--output OUTPUT_DIR] [--prefix PREFIX]

Examples:
    python split-sprite-sheet.py ../../concept/capybara-sprite-walk.png --cols 4 --rows 3 --output ../../frames/walk
    python split-sprite-sheet.py ../../concept/capybara-sprite-run.png --cols 4 --rows 3 --output ../../frames/run --prefix run_
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install dependencies:")
    print("  pip install pillow")
    sys.exit(1)


def split_sprite_sheet(input_path: str, cols: int, rows: int, output_dir: str, prefix: str = "frame_"):
    """
    Split a sprite sheet into individual frame images.

    Args:
        input_path: Path to the sprite sheet image
        cols: Number of columns in the sprite grid
        rows: Number of rows in the sprite grid
        output_dir: Directory to save individual frames
        prefix: Prefix for output filenames (default: "frame_")

    Returns:
        List of output file paths
    """
    # Load sprite sheet
    try:
        img = Image.open(input_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    width, height = img.size
    frame_width = width // cols
    frame_height = height // rows

    print(f"Sprite sheet: {width}x{height} pixels")
    print(f"Grid: {cols} cols x {rows} rows")
    print(f"Frame size: {frame_width}x{frame_height} pixels")
    print(f"Total frames: {cols * rows}")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_files = []
    frame_num = 0

    print(f"\nSplitting frames to: {output_dir}/")

    for row in range(rows):
        for col in range(cols):
            # Calculate crop box
            left = col * frame_width
            top = row * frame_height
            right = left + frame_width
            bottom = top + frame_height

            # Extract frame
            frame = img.crop((left, top, right, bottom))

            # Save frame
            output_filename = f"{prefix}{frame_num:03d}.png"
            output_filepath = output_path / output_filename
            frame.save(output_filepath)
            output_files.append(str(output_filepath))

            print(f"  [{frame_num:2d}] {output_filename} (row {row}, col {col})")
            frame_num += 1

    print(f"\n✓ Successfully split {frame_num} frames!")
    print(f"\nNext steps:")
    print(f"  1. Open Nextion Editor")
    print(f"  2. Go to Picture → Import")
    print(f"  3. Select all frames from: {output_dir}/")
    print(f"  4. Note the picture IDs assigned to each frame")

    return output_files


def main():
    parser = argparse.ArgumentParser(
        description='Split sprite sheet into individual frames for Nextion Editor'
    )
    parser.add_argument(
        'sprite_path',
        help='Path to sprite sheet image file'
    )
    parser.add_argument(
        '--cols',
        type=int,
        required=True,
        help='Number of columns in sprite grid'
    )
    parser.add_argument(
        '--rows',
        type=int,
        required=True,
        help='Number of rows in sprite grid'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./frames',
        help='Output directory for frames (default: ./frames)'
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default='frame_',
        help='Prefix for output filenames (default: frame_)'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.isfile(args.sprite_path):
        print(f"Error: File not found: {args.sprite_path}")
        sys.exit(1)

    # Validate grid dimensions
    if args.cols <= 0 or args.rows <= 0:
        print(f"Error: Grid dimensions must be positive integers")
        sys.exit(1)

    try:
        split_sprite_sheet(
            args.sprite_path,
            args.cols,
            args.rows,
            args.output,
            args.prefix
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
