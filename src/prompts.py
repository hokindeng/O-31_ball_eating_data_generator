"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Animate the black ball moving to eat all red balls. The black ball can only eat red balls that are smaller than or equal to its current size. After eating each red ball, the black ball grows larger. Show smooth movement as the black ball approaches each target, the red ball disappearing when eaten, and the black ball growing after each consumption. Continue until all red balls are eaten and only the large black ball remains.",
        "Show the black ball systematically eating all red balls. The black ball must only attempt to eat red balls that are no larger than itself. Each time a red ball is eaten, it disappears and the black ball grows. Animate the black ball moving smoothly to each target, consuming it, and growing. The sequence continues until all red balls are gone.",
        "Demonstrate the black ball eating all red balls in a valid sequence. The black ball can only eat red balls that are smaller than or equal to its current size. Animate the black ball moving to each target, the red ball vanishing when eaten, and the black ball increasing in size. Continue until all red balls are consumed.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
