import os
import datetime

from controller import DynamixelController
from UI import ExperimentUI
from params import get_trial_moves, STEP_SIZE, THRESHOLD_MM, THRESHOLD_POSITION

def generate_result_file(responses, filename="Results/depth_result.txt", duration_str=""):
    """
    Generate a result file grouped into forward, backward, left, and right trials with mm values.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Prepare sections for all four stages
    sections = {
        "forward": [],
        "backward": [],
        "left": [],
        "right": []
    }

    for res in responses:
        trial = res["trial"]
        pos1, pos2 = res["pos1"], res["pos2"]
        std_idx = res.get("std_idx", 1)
        response = res["response"]
        stage = res.get("stage", "forward")  # Default to forward if missing

        def vec_to_mm(move_vec):
            raw = move_vec[0]
            displacement_mm = (raw - THRESHOLD_POSITION) / STEP_SIZE
            return round(THRESHOLD_MM + displacement_mm, 1)

        mm1 = vec_to_mm(pos1)
        mm2 = vec_to_mm(pos2)

        line = f"Trial {trial}: {mm1}mm vs {mm2}mm  {std_idx}  {response}"

        if stage in sections:
            sections[stage].append(line)
        else:
            print(f"Warning: Unknown stage '{stage}'. Trial {trial} skipped.")

    # Write results
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Experiment duration: {duration_str}\n\n")

        for stage in ["forward", "backward", "left", "right"]:
            if sections[stage]:
                f.write(f"=== {stage.capitalize()} Trials ===\n")
                for line in sections[stage]:
                    f.write(line + "\n")
                f.write("\n")

    print(f"Results saved to {filename}")

def main():
    # ------------------ 记录开始时间 ------------------
    start_time = datetime.datetime.now()

    controller_H = DynamixelController(dxl_id=1, mid_offset=930)  # Horizontal motor
    controller_D = DynamixelController(dxl_id=2, mid_offset=995)  # Directional motor

    D_success = controller_D.initialize()
    H_success = controller_H.initialize()

    if not D_success or not H_success:
        print("One or both motors failed to initialize.")
        return

    ui = None  # 提前定义，避免except里找不到ui
    try:
        pair_count = 4  # Should be even

        # Trials
        forward_trials = get_trial_moves(pair_count, "forward")
        backward_trials = get_trial_moves(pair_count, "backward")
        left_trials = get_trial_moves(pair_count, "left")
        right_trials = get_trial_moves(pair_count, "right")

        # Pre-trials
        forward_pre_trial = [[500, 0], [200, 0]]
        backward_pre_trial = [[-500, 0], [-200, 0]]
        left_pre_trial = [[300, 0], [100, 0]]
        right_pre_trial = [[-300, 0], [-100, 0]]

        trials_dict = {
            "forward": forward_trials,
            "backward": backward_trials,
            "left": left_trials,
            "right": right_trials
        }

        pre_trials_dict = {
            "forward": forward_pre_trial,
            "backward": backward_pre_trial,
            "left": left_pre_trial,
            "right": right_pre_trial
        }

        stages = ["forward", "backward", "left", "right"]

        controller_dict = {
            "forward": controller_D,
            "backward": controller_D,
            "left": controller_H,
            "right": controller_H
        }

        # Create UI
        ui = ExperimentUI(
            controller_dict=controller_dict,
            trials_dict=trials_dict,
            pre_trials_dict=pre_trials_dict,
            stages=stages
        )

        ui.run()

        # ------------------ 记录结束时间 ------------------
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        duration_str = str(duration)

        # Auto timestamp filename + duration in filename (minutes)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        duration_minutes = round(duration.total_seconds() / 60, 1)
        filename = f"Results/Kevin_{timestamp}_{duration_minutes}min.txt"

        generate_result_file(ui.responses, filename=filename, duration_str=duration_str)

    except Exception as e:
        try:
            current_stage = stages[ui.current_stage_idx] if ui else "UI not started"
        except:
            current_stage = "unknown"
        print(f"[ERROR] Experiment failed at stage '{current_stage}' with error: {e}")

    finally:
        controller_D.close()
        controller_H.close()

if __name__ == '__main__':
    main()
