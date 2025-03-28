import random
from typing import List

# Constants for default position and movement step size
DEFAULT_POSITION = 0
STEP_SIZE = 14  # 0.2mm step in raw units (calculation: 630 / 9 / 5)
MIN_MOVEMENT = 329  # corresponds to 4.6mm

"""
Min Movement  = 4.7mm
Max Movement  = 6.3mm
Step Size     = 0.2mm
num_Movements = 9
"""

def calculate_move(distance_mm: float) -> List[int]:
    steps = (distance_mm - 4.7) / 0.2
    x_value = MIN_MOVEMENT + steps * STEP_SIZE
    return [int(round(x_value)), DEFAULT_POSITION]

# Create moves for 4.7mm, 4.9mm, …, 6.3mm
MOVE_VALUES = {round(4.7 + 0.2 * i, 1): calculate_move(4.7 + 0.2 * i) for i in range(9)}

# Define the threshold move at 5.5mm.
THRESHOLD_MOVE = calculate_move(5.5)

def get_trial_moves(pair_count: int) -> List[List[List[int]]]:
    candidate_moves = [MOVE_VALUES[round(4.7 + 0.2 * i, 1)] for i in range(9)]

    trial_moves = []
    for move in candidate_moves:
        for _ in range(pair_count // 2):
            trial_moves.append([THRESHOLD_MOVE, move])
        for _ in range(pair_count // 2):
            trial_moves.append([move, THRESHOLD_MOVE])

    random.shuffle(trial_moves)
    return trial_moves

def main() -> None:
    pair_count = 4  # Ensure this is an even number
    trials = get_trial_moves(pair_count)
    for idx, trial in enumerate(trials, start=1):
        print(f"Trial {idx}: {trial}")

if __name__ == '__main__':
    main()
