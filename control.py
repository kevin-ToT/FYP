from dynamixel_controller import DynamixelController
from experiment_ui import ExperimentUI
from move_params import get_trial_moves, calculate_move, STEP_SIZE

def generate_result_file(responses, filename="results.txt", default_position=0, step_size=STEP_SIZE, threshold_move_value=None):
    """
    生成结果文件，记录每次试次的刺激对和用户选择，格式为：
      Trial 1: 5mm vs 5mm First Greater
      Trial 2: 5mm vs 1mm First Greater
      ...
    """
    if threshold_move_value is None:
        threshold_move_value = calculate_move(5)[0]  # 阈值对应的 raw 值
    with open(filename, "w", encoding="utf-8") as f:
        for res in responses:
            trial = res["trial"]
            pair = res["value"]  # 预期格式为 [[raw_value, 0], [raw_value, 0]]
            response = res["response"]
            mm_values = []
            for move in pair:
                raw = move[0]
                if raw == threshold_move_value:
                    mm = 5
                else:
                    mm = int(round(raw / step_size))
                mm_values.append(mm)
            # 格式：Trial X: {mm1}mm vs {mm2}mm {response}
            f.write(f"Trial {trial}: {mm_values[0]}mm vs {mm_values[1]}mm {response}\n")
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
        pair_count = 2
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
