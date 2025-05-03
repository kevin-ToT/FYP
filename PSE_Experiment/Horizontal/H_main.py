import os

from H_controller import DynamixelController
from H_experiment_ui import ExperimentUI
from H_params import get_trial_moves, STEP_SIZE_MM, STEP_SIZE, THRESHOLD_MM, THRESHOLD_POSITION

def generate_result_file(responses, filename):
    """
    Generate a result file grouped into left/right trials with mm values.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    left_section = []
    right_section = []

    for res in responses:
        trial = res["trial"]
        pair = res["value"]
        response = res["response"]
        stage = res.get("stage", "right")

        mm_values = []
        for move in pair:
            raw = move[0]
            displacement_mm = (raw - THRESHOLD_POSITION) / STEP_SIZE
            mm = round(THRESHOLD_MM + displacement_mm, 1)
            mm_values.append(mm)

        line = f"Trial {trial}: {mm_values[0]}mm vs {mm_values[1]}mm {response}"

        if stage == "left":
            left_section.append(line)
        else:
            right_section.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        if left_section:
            f.write("=== Right Trials ===\n")
            for line in left_section:
                f.write(line + "\n")

        if right_section:
            f.write("\n=== Left Trials ===\n")
            for line in right_section:
                f.write(line + "\n")

    print(f"Results saved to {filename}")


def main():
    controller = DynamixelController()
    if not controller.initialize():
        print("Initialization failed.")
        return

    try:
        # Set up trials for both stages
        pair_count = 4  # Should be even
        left_trials = get_trial_moves(pair_count, "right")
        right_trials = get_trial_moves(pair_count, "left")

        left_pre_trial = [[500, 0], [200, 0]]
        right_pre_trial = [[-500, 0], [-200, 0]]

        # Run UI with both left and right configuration
        ui = ExperimentUI(
            controller=controller,
            left_trials=left_trials,
            right_trials=right_trials,
            left_pre_trial=left_pre_trial,
            right_pre_trial=right_pre_trial
        )
        ui.run()

        # generate_result_file(ui.responses, filename="Results/Kevin_H.txt")
        generate_result_file(ui.responses, filename="Results/Will_H.txt")
    except Exception as e:
        print("An error occurred during the experiment:", e)
    finally:
        controller.close()

if __name__ == '__main__':
    main()
