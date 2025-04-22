import random
from typing import List, Literal

# Constants
STEP_SIZE_MM = 0.2
STEP_SIZE = 600 / 9

DEFAULT_POSITION = 0

THRESHOLD_MM = 5.5
THRESHOLD_POSITION = THRESHOLD_MM * STEP_SIZE

def calculate_move(index: int) -> List[int]:
    displacement_mm = index * STEP_SIZE_MM
    x_value = THRESHOLD_POSITION + displacement_mm * STEP_SIZE
    return [int(round(x_value)), DEFAULT_POSITION]

def backward_move(move: List[int]) -> List[int]:
    return [-move[0], move[1]]

# Precomputed forward movement vectors
MOVE_1 = calculate_move(-4)
MOVE_2 = calculate_move(-3)
MOVE_3 = calculate_move(-2)
MOVE_4 = calculate_move(-1)
THRESHOLD_MOVE = calculate_move(0)
MOVE_6 = calculate_move(1)
MOVE_7 = calculate_move(2)
MOVE_8 = calculate_move(3)
MOVE_9 = calculate_move(4)

# Candidate moves
CANDIDATE_MOVES = [
    MOVE_1, MOVE_2, MOVE_3, MOVE_4, THRESHOLD_MOVE,
    MOVE_6, MOVE_7, MOVE_8, MOVE_9
]

def get_trial_moves(pair_count: int, direction: Literal["forward", "backward"]) -> List[List[List[int]]]:
    """
    Generate trial movement pairs in specified direction: forward or backward.
    
    Args:
        pair_count (int): Number of repetitions per movement.
        direction (str): 'forward' or 'backward'
    
    Returns:
        List of trial movement pairs.
    """
    trial_moves = []

    for move in CANDIDATE_MOVES:
        if direction == "forward":
            main_move = move
            threshold = THRESHOLD_MOVE
        elif direction == "backward":
            main_move = backward_move(move)
            threshold = backward_move(THRESHOLD_MOVE)
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")

        for _ in range(pair_count // 2):
            trial_moves.append([threshold, main_move])
            trial_moves.append([main_move, threshold])

    random.shuffle(trial_moves)
    return trial_moves

def main() -> None:
    pair_count = 2  # Should be even

    print("=== Forward Trials ===")
    forward_trials = get_trial_moves(pair_count, direction="forward")
    for idx, trial in enumerate(forward_trials, start=1):
        print(f"Forward Trial {idx}: {trial}")

    print("\n=== Backward Trials ===")
    backward_trials = get_trial_moves(pair_count, direction="backward")
    for idx, trial in enumerate(backward_trials, start=1):
        print(f"Backward Trial {idx}: {trial}")

if __name__ == '__main__':
    main()
