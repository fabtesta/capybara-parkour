"""
Animation System for Capybara Parkour

Provides classes for managing sprite animations with frame-based timing.
All animation logic runs in Python, Nextion simply displays the frames.
"""

from typing import List, Dict, Optional


class Animation:
    """Represents a single animation sequence"""

    def __init__(self, name: str, frame_ids: List[int], fps: float = 10, loop: bool = True):
        """
        Initialize an animation.

        Args:
            name: Animation identifier (e.g., "walk", "run", "jump")
            frame_ids: List of Nextion picture IDs for this animation
            fps: Frames per second (animation speed)
            loop: Whether animation should loop when it reaches the end
        """
        self.name = name
        self.frame_ids = frame_ids
        self.fps = fps
        self.loop = loop
        self.frame_duration = 1.0 / fps if fps > 0 else 0.1

    def __repr__(self):
        return f"Animation(name={self.name}, frames={len(self.frame_ids)}, fps={self.fps}, loop={self.loop})"


class Sprite:
    """Manages sprite state and animations"""

    def __init__(self, name: str, x: int = 0, y: int = 0):
        """
        Initialize a sprite.

        Args:
            name: Sprite identifier (should match Nextion component name)
            x: Initial X position
            y: Initial Y position
        """
        self.name = name
        self.x = x
        self.y = y
        self.visible = True

        # Animation state
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.current_frame_index = 0
        self.time_in_frame = 0.0
        self.is_playing = False

    def add_animation(self, animation: Animation):
        """Add an animation to this sprite's animation library"""
        self.animations[animation.name] = animation

    def play(self, animation_name: str, restart: bool = True):
        """
        Start playing an animation.

        Args:
            animation_name: Name of the animation to play
            restart: If True, restart animation from beginning even if already playing

        Returns:
            True if animation started, False if animation not found
        """
        if animation_name not in self.animations:
            return False

        # Don't restart if already playing and restart=False
        if not restart and self.current_animation and self.current_animation.name == animation_name:
            return True

        self.current_animation = self.animations[animation_name]
        self.current_frame_index = 0
        self.time_in_frame = 0.0
        self.is_playing = True
        return True

    def stop(self):
        """Stop current animation"""
        self.is_playing = False

    def pause(self):
        """Pause current animation (can be resumed)"""
        self.is_playing = False

    def resume(self):
        """Resume paused animation"""
        if self.current_animation:
            self.is_playing = True

    def update(self, delta_time: float) -> Optional[int]:
        """
        Update animation state based on elapsed time.

        Args:
            delta_time: Time elapsed since last update (in seconds)

        Returns:
            New Nextion picture ID if frame changed, None if no change
        """
        if not self.is_playing or not self.current_animation:
            return None

        self.time_in_frame += delta_time

        # Check if it's time to advance to next frame
        if self.time_in_frame >= self.current_animation.frame_duration:
            self.time_in_frame = 0.0
            self.current_frame_index += 1

            # Handle end of animation
            if self.current_frame_index >= len(self.current_animation.frame_ids):
                if self.current_animation.loop:
                    self.current_frame_index = 0
                else:
                    # Non-looping animation finished, stay on last frame
                    self.current_frame_index = len(self.current_animation.frame_ids) - 1
                    self.is_playing = False

            return self.get_current_frame_id()

        return None

    def get_current_frame_id(self) -> int:
        """Get the current Nextion picture ID for this sprite"""
        if self.current_animation and self.current_animation.frame_ids:
            return self.current_animation.frame_ids[self.current_frame_index]
        return 0

    def set_position(self, x: int, y: int):
        """Update sprite position"""
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int):
        """Move sprite by relative amount"""
        self.x += dx
        self.y += dy

    def show(self):
        """Make sprite visible"""
        self.visible = True

    def hide(self):
        """Make sprite invisible"""
        self.visible = False

    def is_animation_finished(self) -> bool:
        """Check if current non-looping animation has finished"""
        if not self.current_animation:
            return True
        if self.current_animation.loop:
            return False
        return not self.is_playing

    def __repr__(self):
        anim_name = self.current_animation.name if self.current_animation else "None"
        return f"Sprite(name={self.name}, pos=({self.x},{self.y}), anim={anim_name})"


class AnimationManager:
    """Manages multiple sprites and their animations"""

    def __init__(self):
        self.sprites: Dict[str, Sprite] = {}

    def add_sprite(self, sprite: Sprite):
        """Add a sprite to be managed"""
        self.sprites[sprite.name] = sprite

    def remove_sprite(self, name: str):
        """Remove a sprite by name"""
        if name in self.sprites:
            del self.sprites[name]

    def get_sprite(self, name: str) -> Optional[Sprite]:
        """Get a sprite by name"""
        return self.sprites.get(name)

    def update_all(self, delta_time: float) -> Dict[str, int]:
        """
        Update all sprites.

        Args:
            delta_time: Time elapsed since last update

        Returns:
            Dictionary mapping sprite names to new frame IDs (only for sprites that changed)
        """
        frame_updates = {}
        for name, sprite in self.sprites.items():
            new_frame = sprite.update(delta_time)
            if new_frame is not None:
                frame_updates[name] = new_frame
        return frame_updates

    def __repr__(self):
        return f"AnimationManager(sprites={len(self.sprites)})"
