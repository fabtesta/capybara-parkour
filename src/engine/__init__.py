"""
Capybara Parkour Game Engine

Python-based game engine for Raspberry Pi with Nextion display.
"""

from .animation import Animation, Sprite, AnimationManager
from .nextion import NextionDisplay
from .input import InputHandler, GameInput, InputEvent
from .game import Game

__version__ = '0.1.0'
__all__ = [
    'Animation',
    'Sprite',
    'AnimationManager',
    'NextionDisplay',
    'InputHandler',
    'GameInput',
    'InputEvent',
    'Game'
]
