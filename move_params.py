import random
from typing import List

# Constants for default position and movement step size
DEFAULT_POSITION = 0
STEP_SIZE = 66.7  # 600 / 9

def calculate_move(distance_mm: int) -> List[int]:
    x_value = DEFAULT_POSITION + distance_mm * STEP_SIZE
    return [int(round(x_value)), DEFAULT_POSITION]

# Precomputed movement vectors
MOVE_1MM = calculate_move(1)
MOVE_2MM = calculate_move(2)
MOVE_3MM = calculate_move(3)
MOVE_4MM = calculate_move(4)
THRESHOLD_MOVE = calculate_move(5)
MOVE_6MM = calculate_move(6)
MOVE_7MM = calculate_move(7)
MOVE_8MM = calculate_move(8)
MOVE_9MM = calculate_move(9)

def get_trial_moves(pair_count: int) -> List[List[List[int]]]:
    """
    Generate trial movement pairs with the specified number of repetitions per pair.
    Half will be [THRESHOLD_MOVE, move] and half [move, THRESHOLD_MOVE].
    
    Args:
        pair_count (int): Number of times each movement pair should be generated.
    
    Returns:
        List of trial movement pairs.
    """
    candidate_moves = [
        MOVE_1MM, MOVE_2MM, MOVE_3MM, MOVE_4MM, THRESHOLD_MOVE,
        MOVE_6MM, MOVE_7MM, MOVE_8MM, MOVE_9MM
    ]

    trial_moves = []
    for move in candidate_moves:
        for _ in range(pair_count // 2):
            trial_moves.append([THRESHOLD_MOVE, move])
        for _ in range(pair_count // 2):
            trial_moves.append([move, THRESHOLD_MOVE])

    random.shuffle(trial_moves)
    return trial_moves

def main() -> None:
    # Ensure this is an even number
    pair_count = 4  

    trials = get_trial_moves(pair_count)
    for idx, trial in enumerate(trials, start=1):
        print(f"Trial {idx}: {trial}")

if __name__ == '__main__':
    main()
