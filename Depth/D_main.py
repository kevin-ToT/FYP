import os

from D_controller import DynamixelController
from D_experiment_ui import ExperimentUI
from D_params import get_trial_moves, STEP_SIZE_MM, STEP_SIZE, THRESHOLD_MM, THRESHOLD_POSITION

def generate_result_file(responses, filename="Results/depth_result.txt"):
    """
    Generate a result file grouped into forward/backward trials with mm values.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    forward_section = []
    backward_section = []

    for res in responses:
        trial = res["trial"]
        pair = res["value"]
        response = res["response"]
        stage = res.get("stage", "forward")

        mm_values = []
        for move in pair:
            raw = move[0]
            displacement_mm = (raw - THRESHOLD_POSITION) / STEP_SIZE
            mm = round(THRESHOLD_MM + displacement_mm, 1)
            mm_values.append(mm)

        line = f"Trial {trial}: {mm_values[0]}mm vs {mm_values[1]}mm {response}"

        if stage == "forward":
            forward_section.append(line)
        else:
            backward_section.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        if forward_section:
            f.write("=== Forward Trials ===\n")
            for line in forward_section:
                f.write(line + "\n")

        if backward_section:
            f.write("\n=== Backward Trials ===\n")
            for line in backward_section:
                f.write(line + "\n")

    print(f"Results saved to {filename}")


def main():
    controller = DynamixelController()
    if not controller.initialize():
        print("Initialization failed.")
        return

    try:
        # Set up trials for both stages
        pair_count = 2  # Should be even
        forward_trials = get_trial_moves(pair_count, "forward")
        backward_trials = get_trial_moves(pair_count, "backward")

        forward_pre_trial = [[500, 0], [200, 0]]
        backward_pre_trial = [[-500, 0], [-200, 0]]

        # Run UI with both forward and backward configuration
        ui = ExperimentUI(
            controller=controller,
            forward_trials=forward_trials,
            backward_trials=backward_trials,
            forward_pre_trial=forward_pre_trial,
            backward_pre_trial=backward_pre_trial
        )
        ui.run()

        generate_result_file(ui.responses)
    except Exception as e:
        print("An error occurred during the experiment:", e)
    finally:
        controller.close()

if __name__ == '__main__':
    main()
