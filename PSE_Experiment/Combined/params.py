import random
from typing import List, Literal

# ==============================
# Constants
# ==============================

STEP_SIZE_MM = 0.2  # Each step represents 0.2 mm of displacement
STEP_SIZE = 600 / 9  # Scaling factor for position

DEFAULT_POSITION = 0

THRESHOLD_MM = 5.5
THRESHOLD_POSITION = THRESHOLD_MM * STEP_SIZE

# ==============================
# Helper Functions
# ==============================

def calculate_move(index: int) -> List[int]:
    """
    Calculates the move position based on the step index.
    """
    displacement_mm = index * STEP_SIZE_MM
    x_value = THRESHOLD_POSITION + displacement_mm * STEP_SIZE
    return [int(round(x_value)), DEFAULT_POSITION]

def opposite_move(move: List[int]) -> List[int]:
    """
    Returns the move mirrored in the opposite direction.
    """
    return [-move[0], move[1]]

# ==============================
# Precomputed Moves
# ==============================

# Precompute positions for moves ranging from -4 to +4 steps
MOVE_1 = calculate_move(-4)
MOVE_2 = calculate_move(-3)
MOVE_3 = calculate_move(-2)
MOVE_4 = calculate_move(-1)
THRESHOLD_MOVE = calculate_move(0)
MOVE_6 = calculate_move(1)
MOVE_7 = calculate_move(2)
MOVE_8 = calculate_move(3)
MOVE_9 = calculate_move(4)

# List of all candidate moves
CANDIDATE_MOVES = [
    MOVE_1, MOVE_2, MOVE_3, MOVE_4, THRESHOLD_MOVE,
    MOVE_6, MOVE_7, MOVE_8, MOVE_9
]

# ==============================
# Trial Generation Function
# ==============================

def get_trial_moves(pair_count: int, direction: Literal["forward", "backward", "left", "right"]) -> List[List[List[int]]]:
    """
    Generates trial movement pairs for the given direction.

    Each move generates two trials:
    - threshold -> move (label 1)
    - move -> threshold (label 2)
    """
    trial_moves = []

    for move in CANDIDATE_MOVES:

        # Determine main move and threshold based on direction
        if direction in ["forward", "right"]:
            main_move = move
            threshold = THRESHOLD_MOVE
        elif direction in ["backward", "left"]:
            main_move = opposite_move(move)
            threshold = opposite_move(THRESHOLD_MOVE)
        else:
            raise ValueError("Direction must be 'forward', 'backward', 'left', or 'right'")

        # For each move, create pair_count/2 repetitions of both trial orders
        for _ in range(pair_count // 2):
            trial_moves.append([threshold, main_move, 1])  # Threshold first
            trial_moves.append([main_move, threshold, 2])  # Move first

    random.shuffle(trial_moves)
    return trial_moves

# ==============================
# Main Function
# ==============================

def main() -> None:
    pair_count = 2  # Must be even

    random.seed(42)  # For reproducible shuffling

    directions = ["forward", "backward", "right", "left"]

    for direction in directions:
        print(f"\n=== {direction.capitalize()} Trials ===")
        trials = get_trial_moves(pair_count, direction=direction)
        for idx, trial in enumerate(trials, start=1):
            print(f"{direction.capitalize()} Trial {idx}: {trial}")

# ==============================
# Entry Point
# ==============================

if __name__ == '__main__':
    main()
