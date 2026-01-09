"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK GENERATOR                                 ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to implement your data generation logic.                 ║
║  Replace the example implementation with your own task.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import math
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Black Ball Eats Red Balls task generator.
    
    Generates tasks where a black ball must eat all red balls in a valid sequence.
    The black ball can only eat red balls that are smaller than or equal to its current size.
    After eating, the black ball grows by a fixed multiplicative factor.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled (using mp4 format)
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one task pair."""
        
        # Generate task data (ball sizes, positions, eating sequence)
        task_data = self._generate_task_data()
        
        # Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        # Select prompt
        prompt = get_prompt(task_data.get("type", "default"))
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_task_data(self) -> dict:
        """
        Generate a solvable ball eating task.
        
        Returns:
            dict with keys:
                - black_ball: dict with 'size', 'x', 'y'
                - red_balls: list of dicts with 'size', 'x', 'y', 'id'
                - eating_sequence: list of red ball IDs in order
                - type: str
        """
        # Random number of red balls
        num_red_balls = random.randint(
            self.config.min_red_balls,
            self.config.max_red_balls
        )
        
        # Generate solvable ball sizes
        black_size, red_sizes, eating_sequence = self._generate_solvable_sizes(
            num_red_balls
        )
        
        # Generate positions (non-overlapping)
        width, height = self.config.image_size
        black_pos = self._generate_position(black_size, width, height, [])
        red_positions = []
        occupied = [{
            'x': black_pos[0],
            'y': black_pos[1],
            'radius': black_size / 2
        }]
        
        for i, red_size in enumerate(red_sizes):
            pos = self._generate_position(red_size, width, height, occupied)
            red_positions.append({
                'x': pos[0],
                'y': pos[1],
                'size': red_size,
                'id': i
            })
            occupied.append({
                'x': pos[0],
                'y': pos[1],
                'radius': red_size / 2
            })
        
        return {
            'black_ball': {
                'size': black_size,
                'x': black_pos[0],
                'y': black_pos[1]
            },
            'red_balls': red_positions,
            'eating_sequence': eating_sequence,
            'type': 'default'
        }
    
    def _generate_solvable_sizes(
        self,
        num_red_balls: int
    ) -> Tuple[float, List[float], List[int]]:
        """
        Generate ball sizes that guarantee a solvable eating sequence.
        
        Algorithm: Work backwards from the final state.
        Start with the final black ball size, then work backwards
        to determine what sizes the red balls must have been.
        
        Returns:
            (black_initial_size, red_sizes_list, eating_sequence)
        """
        growth_factor = self.config.growth_factor
        min_size = self.config.min_ball_size
        max_size = self.config.max_ball_size
        
        # Start with a reasonable final black ball size
        final_black_size = random.uniform(
            max_size * 0.6,
            max_size * 0.9
        )
        
        # Work backwards: what was the size before eating the last red ball?
        # final_size = (previous_size) * growth_factor
        # previous_size = final_size / growth_factor
        current_black_size = final_black_size
        
        # Build red ball sizes in reverse order
        red_sizes_reverse = []
        
        for _ in range(num_red_balls):
            # The red ball that was just eaten must be <= current_black_size
            # Choose a size that's reasonable but ensures solvability
            max_red_size = current_black_size
            min_red_size = max(min_size, current_black_size * 0.3)
            
            red_size = random.uniform(min_red_size, max_red_size)
            red_sizes_reverse.append(red_size)
            
            # Before eating this red ball, black ball was smaller
            current_black_size = current_black_size / growth_factor
        
        # Reverse to get forward order
        red_sizes = list(reversed(red_sizes_reverse))
        initial_black_size = current_black_size
        
        # Ensure initial black size is within bounds
        if initial_black_size < min_size:
            # Scale everything up
            scale = min_size / initial_black_size
            initial_black_size = min_size
            red_sizes = [s * scale for s in red_sizes]
            final_black_size = final_black_size * scale
        
        if initial_black_size > max_size * 0.5:
            # Scale everything down
            scale = (max_size * 0.5) / initial_black_size
            initial_black_size = initial_black_size * scale
            red_sizes = [s * scale for s in red_sizes]
            final_black_size = final_black_size * scale
        
        # Ensure all sizes are within bounds
        for i in range(len(red_sizes)):
            red_sizes[i] = max(min_size, min(max_size, red_sizes[i]))
        initial_black_size = max(min_size, min(max_size * 0.5, initial_black_size))
        
        # Ensure initial black ball can eat at least one red ball
        min_red_size = min(red_sizes) if red_sizes else min_size
        if initial_black_size < min_red_size:
            initial_black_size = min_red_size
        
        # Generate eating sequence using greedy algorithm to ensure solvability
        eating_sequence = self._compute_eating_sequence(
            initial_black_size, red_sizes, growth_factor
        )
        
        # Verify solvability (should always pass with our algorithm)
        if not self._verify_solvability(initial_black_size, red_sizes, eating_sequence, growth_factor):
            # If verification fails, retry generation (with recursion limit)
            # This should rarely happen, but handle it gracefully
            return self._generate_solvable_sizes(num_red_balls)
        
        return initial_black_size, red_sizes, eating_sequence
    
    def _compute_eating_sequence(
        self,
        initial_black_size: float,
        red_sizes: List[float],
        growth_factor: float
    ) -> List[int]:
        """
        Compute a valid eating sequence using greedy algorithm.
        
        At each step, eat the largest red ball that is <= current black size.
        This ensures a valid sequence exists.
        """
        current_size = initial_black_size
        remaining = set(range(len(red_sizes)))
        sequence = []
        
        while remaining:
            # Find the largest red ball that can be eaten
            candidates = [
                (red_sizes[i], i) for i in remaining
                if red_sizes[i] <= current_size
            ]
            
            if not candidates:
                # No valid candidate - this shouldn't happen with proper generation
                # Fallback: sort by size (smallest first)
                candidates = [(red_sizes[i], i) for i in remaining]
                candidates.sort(key=lambda x: x[0])
                if candidates[0][0] > current_size:
                    # Still can't eat - return best effort sequence
                    break
            
            # Eat the largest candidate
            candidates.sort(key=lambda x: x[0], reverse=True)
            _, red_idx = candidates[0]
            sequence.append(red_idx)
            remaining.remove(red_idx)
            current_size = current_size * growth_factor
        
        # Add any remaining balls (shouldn't happen, but handle gracefully)
        for red_idx in remaining:
            sequence.append(red_idx)
        
        return sequence
    
    def _verify_solvability(
        self,
        initial_black_size: float,
        red_sizes: List[float],
        eating_sequence: List[int],
        growth_factor: float
    ) -> bool:
        """Verify that the eating sequence is valid."""
        if len(eating_sequence) != len(red_sizes):
            return False
        
        current_size = initial_black_size
        
        for red_idx in eating_sequence:
            red_size = red_sizes[red_idx]
            if red_size > current_size:
                return False
            current_size = current_size * growth_factor
        
        return True
    
    def _generate_position(
        self,
        ball_size: float,
        width: int,
        height: int,
        occupied: List[dict]
    ) -> Tuple[float, float]:
        """Generate a position that doesn't overlap with existing balls."""
        radius = ball_size / 2
        margin = radius + 10  # Extra margin
        
        for _ in range(100):  # Try up to 100 times
            x = random.uniform(margin, width - margin)
            y = random.uniform(margin, height - margin)
            
            # Check overlap
            overlaps = False
            for other in occupied:
                dx = x - other['x']
                dy = y - other['y']
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < (radius + other['radius'] + 5):  # 5px buffer
                    overlaps = True
                    break
            
            if not overlaps:
                return (x, y)
        
        # Fallback: return center if can't find non-overlapping position
        return (width / 2, height / 2)
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state with black ball and all red balls."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw red balls
        for red_ball in task_data['red_balls']:
            self._draw_ball(
                draw,
                red_ball['x'],
                red_ball['y'],
                red_ball['size'],
                color=(255, 0, 0)  # Red
            )
        
        # Draw black ball
        black = task_data['black_ball']
        self._draw_ball(
            draw,
            black['x'],
            black['y'],
            black['size'],
            color=(0, 0, 0)  # Black
        )
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state with only the large black ball."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Calculate final black ball size
        black = task_data['black_ball']
        growth_factor = self.config.growth_factor
        num_red = len(task_data['red_balls'])
        final_size = black['size'] * (growth_factor ** num_red)
        
        # Draw final black ball (centered)
        width, height = self.config.image_size
        self._draw_ball(
            draw,
            width / 2,
            height / 2,
            final_size,
            color=(0, 0, 0)  # Black
        )
        
        return img
    
    def _draw_ball(
        self,
        draw: ImageDraw.Draw,
        x: float,
        y: float,
        size: float,
        color: Tuple[int, int, int]
    ):
        """Draw a filled circle representing a ball."""
        radius = size / 2
        bbox = [
            x - radius,
            y - radius,
            x + radius,
            y + radius
        ]
        draw.ellipse(bbox, fill=color, outline=None)
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> Optional[str]:
        """Generate ground truth video showing the eating sequence."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames (already limited to <= 10 seconds)
        frames = self._create_animation_frames(task_data)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_animation_frames(self, task_data: dict) -> List[Image.Image]:
        """
        Create animation frames showing the black ball eating all red balls.
        
        Returns list of PIL Images.
        """
        frames = []
        width, height = self.config.image_size
        growth_factor = self.config.growth_factor
        
        black = task_data['black_ball']
        red_balls = task_data['red_balls']
        eating_sequence = task_data['eating_sequence']
        
        # Create a mapping from red ball ID to red ball data
        red_dict = {ball['id']: ball for ball in red_balls}
        
        # Initial state: hold for a moment
        current_black_size = black['size']
        current_black_x = black['x']
        current_black_y = black['y']
        remaining_reds = set(ball['id'] for ball in red_balls)
        
        # Calculate frames per action to ensure video <= 10 seconds
        max_frames = int(self.config.max_video_duration * self.config.video_fps)
        num_actions = len(eating_sequence)
        # Reserve frames: initial hold + final hold
        reserved_frames = 8
        available_frames = max_frames - reserved_frames
        frames_per_action = max(3, available_frames // (num_actions * 2))  # move + grow per action
        
        hold_frames = 4
        for _ in range(hold_frames):
            frames.append(self._render_frame(
                current_black_x, current_black_y, current_black_size,
                remaining_reds, red_dict
            ))
        
        # For each red ball in the eating sequence
        move_frames_per_ball = max(3, frames_per_action)
        # Growth animation: 6-12 frames for smooth transition
        grow_frames = min(12, max(6, frames_per_action))
        
        for red_id in eating_sequence:
            target_red = red_dict[red_id]
            target_x = target_red['x']
            target_y = target_red['y']
            
            # Move black ball towards target
            for i in range(move_frames_per_ball):
                progress = i / (move_frames_per_ball - 1) if move_frames_per_ball > 1 else 1.0
                current_x = current_black_x + (target_x - current_black_x) * progress
                current_y = current_black_y + (target_y - current_black_y) * progress
                
                frames.append(self._render_frame(
                    current_x, current_y, current_black_size,
                    remaining_reds, red_dict
                ))
            
            # Save old size before growth
            old_size = current_black_size
            # Calculate new size after eating
            new_size = old_size * growth_factor
            
            # Remove red ball
            remaining_reds.remove(red_id)
            current_black_x = target_x
            current_black_y = target_y
            
            # Show growth animation: smooth monotonic transition from old_size to new_size
            for i in range(grow_frames):
                progress = i / (grow_frames - 1) if grow_frames > 1 else 1.0
                # Linear interpolation: monotonically increasing from old_size to new_size
                # Ensure no overshoot: size never exceeds new_size
                size = old_size + (new_size - old_size) * progress
                # Clamp to ensure no overshoot (shouldn't be needed with linear interpolation, but safety check)
                size = min(size, new_size)
                
                frames.append(self._render_frame(
                    current_black_x, current_black_y, size,
                    remaining_reds, red_dict
                ))
            
            # Update black ball state to final size
            current_black_size = new_size
        
        # Hold final state
        final_hold_frames = 4
        for _ in range(final_hold_frames):
            frames.append(self._render_frame(
                current_black_x, current_black_y, current_black_size,
                remaining_reds, red_dict
            ))
        
        # Ensure we don't exceed max frames
        max_frames = int(self.config.max_video_duration * self.config.video_fps)
        if len(frames) > max_frames:
            # Sample frames evenly to fit within limit
            indices = [int(i * (len(frames) - 1) / (max_frames - 1)) for i in range(max_frames)]
            frames = [frames[i] for i in indices]
        
        return frames
    
    def _render_frame(
        self,
        black_x: float,
        black_y: float,
        black_size: float,
        remaining_red_ids: set,
        red_dict: dict
    ) -> Image.Image:
        """Render a single animation frame."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw remaining red balls
        for red_id in remaining_red_ids:
            red_ball = red_dict[red_id]
            self._draw_ball(
                draw,
                red_ball['x'],
                red_ball['y'],
                red_ball['size'],
                color=(255, 0, 0)  # Red
            )
        
        # Draw black ball
        self._draw_ball(
            draw,
            black_x,
            black_y,
            black_size,
            color=(0, 0, 0)  # Black
        )
        
        return img
