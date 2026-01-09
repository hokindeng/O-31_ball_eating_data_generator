"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           BALL EATING TASK CONFIGURATION                      ║
║                                                                               ║
║  Configuration for Ball Eating Sequence Task.                                ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Ball Eating task configuration.
    
    Task: Black ball must eat all red balls in valid size-constrained sequence.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="ball_eating")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    min_red_balls: int = Field(default=2, description="Minimum number of red balls")
    max_red_balls: int = Field(default=6, description="Maximum number of red balls")
    growth_factor: float = Field(default=1.4, description="Multiplicative growth factor after eating")
    min_ball_size: int = Field(default=20, description="Minimum ball size in pixels")
    max_ball_size: int = Field(default=150, description="Maximum ball size in pixels")
    max_video_duration: float = Field(default=10.0, description="Maximum video duration in seconds")
