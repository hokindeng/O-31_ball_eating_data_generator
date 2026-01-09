# Ball Eating Task Generator 🎯

A data generator for creating synthetic reasoning tasks where a black ball must eat all red balls in a valid sequence. The black ball can only eat red balls that are smaller than or equal to its current size, and grows larger after each consumption.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/ball-eating-generator.git
cd ball-eating-generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📋 Task Description

The **Ball Eating Task** is a reasoning task where:

- **Initial State**: A black ball and multiple red balls are placed on a canvas
- **Goal**: The black ball must eat all red balls
- **Constraint**: The black ball can only eat red balls that are **smaller than or equal to** its current size
- **Growth**: After eating each red ball, the black ball grows by a multiplicative factor (default: 1.4x)
- **Challenge**: Find a valid eating sequence that allows the black ball to consume all red balls

The generator ensures all generated tasks are **solvable** by using a backward-solving algorithm that guarantees a valid sequence exists.

---

## 📁 Project Structure

```
template-data-generator-eatballs/
├── core/                    # Core utilities (framework code)
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image rendering helpers
│   ├── video_utils.py      # Video generation utilities
│   └── output_writer.py    # File output management
├── src/                     # Task-specific implementation
│   ├── generator.py        # Ball eating task generator
│   ├── prompts.py          # Task instruction prompts
│   └── config.py           # Task configuration
├── examples/
│   └── generate.py         # Entry point script
└── data/                    # Generated output
    └── my_task/
        └── ball_eating_task/
            └── ball_eating_0000/
                ├── first_frame.png
                ├── final_frame.png
                ├── prompt.txt
                └── ground_truth.mp4
```

---

## 📦 Output Format

Each generated task produces:

```
data/my_task/ball_eating_task/{task_id}/
├── first_frame.png          # Initial state: black ball + all red balls
├── final_frame.png          # Final state: large black ball only
├── prompt.txt               # Task instructions
└── ground_truth.mp4         # Solution animation video (≤10 seconds)
```

### Output Details

- **first_frame.png**: Shows the initial state with the black ball and all red balls at their starting positions
- **final_frame.png**: Shows the final state with only the large black ball (after eating all red balls)
- **prompt.txt**: Contains instructions describing the task and constraints
- **ground_truth.mp4**: Animated video showing the solution sequence with:
  - Smooth movement of the black ball to each target
  - Red ball disappearing when eaten
  - Smooth, monotonic growth animation (6-12 frames per growth)
  - Maximum duration of 10 seconds

---

## ⚙️ Configuration

All task parameters are configured in `src/config.py`:

```python
class TaskConfig(GenerationConfig):
    domain: str = "ball_eating"
    image_size: tuple[int, int] = (512, 512)
    
    # Task-specific parameters
    min_red_balls: int = 2          # Minimum number of red balls
    max_red_balls: int = 6          # Maximum number of red balls
    growth_factor: float = 1.4      # Size multiplier after eating
    min_ball_size: int = 20         # Minimum ball size (pixels)
    max_ball_size: int = 150        # Maximum ball size (pixels)
    
    # Video settings
    generate_videos: bool = True
    video_fps: int = 10
    max_video_duration: float = 10.0  # Maximum video length (seconds)
```

---

## 🎬 Generation Algorithm

The generator uses a **backward-solving approach** to ensure all tasks are solvable:

1. **Size Generation**: Start with a target final black ball size, then work backwards to determine initial sizes
2. **Sequence Computation**: Use a greedy algorithm to compute a valid eating sequence
3. **Position Generation**: Place balls randomly while avoiding overlaps
4. **Animation**: Generate smooth animations with:
   - Linear interpolation for movement
   - Monotonic size growth (no overshoot)
   - 6-12 frame transitions for each growth event

### Key Features

- ✅ **Guaranteed Solvability**: All generated tasks have valid solutions
- ✅ **Smooth Animations**: Growth animations are monotonic and smooth
- ✅ **No Overshoot**: Black ball size never exceeds target size during growth
- ✅ **Video Length Control**: All videos are capped at 10 seconds

---

## 📝 Usage Examples

### Generate 100 tasks

```bash
python examples/generate.py --num-samples 100
```

### Generate with custom output directory

```bash
python examples/generate.py --num-samples 50 --output data/my_custom_output
```

### Generate without videos

```bash
python examples/generate.py --num-samples 50 --no-videos
```

### Generate with specific random seed

```bash
python examples/generate.py --num-samples 50 --seed 42
```

---

## 🔧 Command Line Options

```bash
python examples/generate.py --help
```

Options:
- `--num-samples`: Number of task samples to generate (required)
- `--output`: Output directory (default: `data/questions`)
- `--seed`: Random seed for reproducibility (optional)
- `--no-videos`: Disable video generation

---

## 📚 Dependencies

See `requirements.txt` for the complete list. Main dependencies:

- `numpy`: Numerical operations
- `Pillow`: Image processing
- `pydantic`: Configuration management
- `opencv-python`: Video generation

---

## 🎯 Task Constraints

The generated tasks enforce the following constraints:

1. **Size Constraint**: Black ball can only eat red balls ≤ its current size
2. **Growth Constraint**: After eating, black ball grows by `growth_factor`
3. **Solvability**: All tasks are guaranteed to have at least one valid solution
4. **Animation Quality**: 
   - Growth animations are smooth and monotonic
   - No size overshoot during growth transitions
   - 6-12 frames per growth event for smoothness

---

## 📄 License

See `LICENSE` file for details.
