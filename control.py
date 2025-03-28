from dynamixel_controller import DynamixelController
from experiment_ui import ExperimentUI
from move_params import get_trial_moves, STEP_SIZE, MIN_MOVEMENT, THRESHOLD_MOVE

def generate_result_file(responses, filename="results.txt", min_movement=MIN_MOVEMENT, threshold_move_value=THRESHOLD_MOVE[0], step_size=STEP_SIZE):
    with open(filename, "w", encoding="utf-8") as f:
        for res in responses:
            trial = res["trial"]
            pair = res["value"]
            response = res["response"]
            mm_values = []
            for move in pair:
                raw_value = move[0]
                if raw_value == threshold_move_value:
                    mm = 5.5
                else:
                    steps = (raw_value - min_movement) / step_size
                    mm = 4.7 + steps * 0.2
                    mm = round(mm, 1)
                mm_values.append(mm)
            f.write(f"Trial {trial}: {mm_values[0]} vs {mm_values[1]} {response}\n")
    print(f"Results saved to {filename}")


def main():
    controller = DynamixelController()
    if not controller.initialize():
        print("Initialization failed.")
        return

    try:
        pre_trial_move_value = [
            [500, 0], 
            [200, 0] 
        ]

        # pair_count (even number)
        pair_count = 6
        trial_move_values = get_trial_moves(pair_count)
        max_trial = len(trial_move_values)

        ui = ExperimentUI(controller=controller,
                          pre_trial_move_value=pre_trial_move_value,
                          trial_move_values=trial_move_values,
                          max_trial=max_trial)
        ui.run()

        generate_result_file(ui.responses)
    except Exception as e:
        print("An error occurred during the experiment:", e)
    finally:
        controller.close()

if __name__ == '__main__':
    main()
