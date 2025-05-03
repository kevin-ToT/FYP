import tkinter as tk
from typing import List
from params import get_trial_moves

# Dummy controller for testing
class DummyController:
    def read_current_position(self):
        print("Dummy: 读取当前电机位置")
        return 500

    def move_to_position(self, positions: List[int]):
        print("Dummy: 正在移动到位置:", positions)

class ExperimentUI:
    def __init__(self, controller_dict=None,
                 trials_dict=None, pre_trials_dict=None,
                 stages=None):
        self.controller_dict = controller_dict
        self.root = tk.Tk()
        self.root.title("Interactive UI")
        self.root.geometry("1280x720")

        self.stages = stages  # List of stage names in order
        self.current_stage_idx = 0
        self.trial_count = 0
        self.responses = []

        self.trials_dict = trials_dict
        self.pre_trials_dict = pre_trials_dict

        # Initialize with first stage's trials
        self._load_stage(self.stages[self.current_stage_idx])

        self.phase_stage = 0

        # ------------------ UI Pages ------------------
        self.main_frame = tk.Frame(self.root)
        self.pre_trial_frame = tk.Frame(self.root)
        self.trial_frame = tk.Frame(self.root)
        self.rest_frame = tk.Frame(self.root)
        self.final_frame = tk.Frame(self.root)

        # ----- Welcome page -----
        self.main_frame.pack(expand=True, fill='both')
        tk.Label(self.main_frame, text="Welcome! Click Start to begin.", font=("Helvetica", 28)).pack(pady=(120, 30))
        tk.Button(self.main_frame, text="Start the Experiment", command=self.start_experiment,
                  font=("Helvetica", 24), padx=20, pady=10).pack()

        # ----- Pre-trial page -----
        self.pre_trial_label = tk.Label(self.pre_trial_frame, font=("Helvetica", 24), wraplength=1000)
        self.pre_trial_label.pack(pady=50)
        button_frame = tk.Frame(self.pre_trial_frame)
        button_frame.pack(pady=20)
        self.l_button = tk.Button(button_frame, text="First Greater", font=("Helvetica", 24), state=tk.DISABLED,
                                  command=self.show_result)
        self.l_button.pack(side=tk.LEFT, padx=10)
        self.s_button = tk.Button(button_frame, text="Second Greater", font=("Helvetica", 24), state=tk.DISABLED,
                                  command=self.show_result)
        self.s_button.pack(side=tk.LEFT, padx=10)
        self.result_label = tk.Label(self.pre_trial_frame, font=("Helvetica", 28))
        self.result_label.pack(pady=20)

        # ----- Trial page -----
        self.trial_label = tk.Label(self.trial_frame, font=("Helvetica", 24), wraplength=1000)
        self.trial_label.pack(pady=50)
        button_frame_trial = tk.Frame(self.trial_frame)
        button_frame_trial.pack(pady=20)
        self.option1_button = tk.Button(button_frame_trial, text="First Greater", font=("Helvetica", 24), width=12,
                                        command=lambda: self.handle_trial_response("First Greater"), state=tk.DISABLED)
        self.option1_button.pack(side=tk.LEFT, padx=10)
        self.option3_button = tk.Button(button_frame_trial, text="Second Greater", font=("Helvetica", 24), width=12,
                                        command=lambda: self.handle_trial_response("Second Greater"), state=tk.DISABLED)
        self.option3_button.pack(side=tk.LEFT, padx=10)

        # ----- Rest page -----
        self.rest_label = tk.Label(self.rest_frame,
                                   text="Stage completed.\n\nPlease rest.\n\nPress SPACE to continue.",
                                   font=("Helvetica", 26), wraplength=1000)
        self.rest_label.pack(pady=100)

        # ----- Final page -----
        self.final_label = tk.Label(self.final_frame, text="Thank you.", font=("Helvetica", 28), wraplength=1000)
        self.final_label.pack(pady=100)
        tk.Button(self.final_frame, text="Exit", font=("Helvetica", 24), command=self.root.quit).pack(pady=20)

    def _load_stage(self, stage_name):
        self.current_stage = stage_name
        self.trial_move_values = self.trials_dict[stage_name]
        self.pre_trial_move_value = self.pre_trials_dict[stage_name]
        self.current_controller = self.controller_dict[stage_name]  # SELECT CONTROLLER
        self.MAX_TRIALS = len(self.trial_move_values)
        self.trial_count = 0


    def start_experiment(self):
        self.main_frame.pack_forget()
        self.show_pre_trial_page()

    def show_pre_trial_page(self):
        self.pre_trial_frame.pack(expand=True, fill='both')
        self.phase_stage = 0
        self.l_button.config(state=tk.DISABLED)
        self.s_button.config(state=tk.DISABLED)
        self.result_label.config(text="")
        self.pre_trial_label.config(
            text=f"This is a practice for {self.current_stage}.\n\nPress SPACE for the first stimulation.")
        self.root.bind("<space>", self.handle_pre_trial_space)

    def handle_pre_trial_space(self, event):
        if self.phase_stage == 0:
            self.pre_trial_label.config(
                text="\n\n First stimulation triggered. Press SPACE for the second stimulation.")
            self.current_controller.move_to_position(self.pre_trial_move_value[0])
            self.phase_stage = 1
        elif self.phase_stage == 1:
            self.pre_trial_label.config(
                text="\n\n Second stimulation triggered. Now please make your choice.")
            self.current_controller.move_to_position(self.pre_trial_move_value[1])
            self.phase_stage = 2
            self.l_button.config(state=tk.NORMAL)
            self.s_button.config(state=tk.NORMAL)

    def show_result(self):
        self.result_label.config(
            text="Pre-experiment finished. Let's proceed to the formal experiment.")
        self.root.after(4000, self.goto_trial_page)

    def goto_trial_page(self):
        self.pre_trial_frame.pack_forget()
        self.show_trial_page()

    def show_trial_page(self):
        self.trial_frame.pack(expand=True, fill='both')
        if self.trial_count < self.MAX_TRIALS:
            self.current_trial_pair = self.trial_move_values[self.trial_count]
        self.phase_stage = 0
        self.option1_button.config(state=tk.DISABLED)
        self.option3_button.config(state=tk.DISABLED)
        self.root.bind("<space>", self.handle_trial_space)
        self.trial_label.config(
            text=f"{self.current_stage.capitalize()} Trial {self.trial_count + 1}/{self.MAX_TRIALS}:\n\nPress SPACE for the first stimulation.")

    def handle_trial_space(self, event):
        if self.phase_stage == 0:
            self.trial_label.config(
                text=f"{self.current_stage.capitalize()} Trial {self.trial_count + 1}/{self.MAX_TRIALS}:\n\nFirst stimulation triggered. Press SPACE for the second stimulation.")
            self.current_controller.move_to_position(self.current_trial_pair[0])
            self.phase_stage = 1
        elif self.phase_stage == 1:
            self.trial_label.config(
                text=f"{self.current_stage.capitalize()} Trial {self.trial_count + 1}/{self.MAX_TRIALS}:\n\nSecond stimulation triggered. Now please make your choice.")
            self.current_controller.move_to_position(self.current_trial_pair[1])
            self.phase_stage = 2
            self.option1_button.config(state=tk.NORMAL)
            self.option3_button.config(state=tk.NORMAL)

    def handle_trial_response(self, response):
        self.responses.append({
            "trial": self.trial_count + 1,
            "value": self.current_trial_pair,
            "response": response,
            "stage": self.current_stage
        })
        self.trial_count += 1
        self.trial_frame.pack_forget()
        self.root.unbind("<space>")
        if self.trial_count < self.MAX_TRIALS:
            self.show_trial_page()
        else:
            self.show_rest_page_or_finish()

    def show_rest_page_or_finish(self):
        if self.current_stage_idx + 1 < len(self.stages):
            self.rest_frame.pack(expand=True, fill='both')
            self.rest_label.config(text=f"{self.current_stage.capitalize()} trials completed. \n\nPlease rest.\n\nPress SPACE to continue the trials.")
            self.root.bind("<space>", self.handle_rest_space)
        else:
            self.show_final_page()


    def handle_rest_space(self, event):
        self.rest_frame.pack_forget()
        self.root.unbind("<space>")
        self.current_stage_idx += 1
        if self.current_stage_idx < len(self.stages):
            next_stage = self.stages[self.current_stage_idx]
            self._load_stage(next_stage)
            self.show_pre_trial_page()
        else:
            self.show_final_page()

    def show_final_page(self):
        self.final_frame.pack(expand=True, fill='both')

    def run(self):
        if self.current_controller:
            current_pos = self.current_controller.read_current_position()
            self.current_controller.move_to_position([current_pos, 0])

        self.root.mainloop()

# ---------------------- Example Usage -------------------------

if __name__ == '__main__':
    dummy_controller = DummyController()

    pair_count = 2

    forward_trials = get_trial_moves(pair_count, direction="forward")
    backward_trials = get_trial_moves(pair_count, direction="backward")
    left_trials = get_trial_moves(pair_count, direction="left")
    right_trials = get_trial_moves(pair_count, direction="right")

    forward_pre_trial = [[500, 0], [100, 0]]
    backward_pre_trial = [[-500, 0], [-100, 0]]
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
        "forward": dummy_controller,
        "backward": dummy_controller,
        "left": dummy_controller,
        "right": dummy_controller
    }

    ui = ExperimentUI(controller_dict=controller_dict,
                    trials_dict=trials_dict,
                    pre_trials_dict=pre_trials_dict,
                    stages=stages)

    ui.run()
