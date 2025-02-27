import tkinter as tk
from move_params import get_trial_moves

# DummyController for testing
class DummyController:
    def read_current_position(self):
        print("Dummy: 读取当前电机位置")
        return 500

    def move_to_position(self, positions):
        print("Dummy: 正在移动到位置:", positions)


class ExperimentUI:
    def __init__(self, controller=None, pre_trial_move_value=None, trial_move_values=None, max_trial=None):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Interactive UI")
        self.root.geometry("1280x720")

        # 记录实验试次和最大试次数
        self.trial_count = 0
        self.MAX_TRIALS = max_trial

        # 用于记录每一次试次的结果
        self.responses = []

        self.pre_trial_move_value = pre_trial_move_value
        self.trial_move_values = trial_move_values

        # 用于控制阶段的进度（在预实验和正式实验阶段分别使用）
        self.phase_stage = 0

        # 定义各个页面（Frame）
        self.main_frame = tk.Frame(self.root)         # 欢迎页
        self.pre_trial_frame = tk.Frame(self.root)      # 预试次页面
        self.trial_frame = tk.Frame(self.root)          # 试次页面
        self.final_frame = tk.Frame(self.root)          # 实验结束页面

        # ----- 欢迎页 -----
        self.main_frame.pack(expand=True, fill='both')
        self.welcome_label = tk.Label(
            self.main_frame, 
            text="Welcome! Click Start to begin.", 
            font=("Helvetica", 28)
        )
        self.welcome_label.pack(pady=(120, 30))
        self.start_button = tk.Button(
            self.main_frame,
            text="Start the Experiment",
            command=self.start_experiment,
            font=("Helvetica", 24),
            padx=20, pady=10
        )
        self.start_button.pack()

        # ----- 预试次页面 -----
        self.pre_trial_label = tk.Label(
            self.pre_trial_frame,
            text="This is a practice.\n\nPress SPACE to receive the first stimulation.",
            font=("Helvetica", 24),
            wraplength=1000
        )
        self.pre_trial_label.pack(pady=50)

        button_frame = tk.Frame(self.pre_trial_frame)
        button_frame.pack(pady=20)
        
        # 两个选择按钮，用于预实验阶段结束时的响应，初始禁用
        self.l_button = tk.Button(
            button_frame,
            text="First Greater",
            command=self.show_result,
            font=("Helvetica", 24),
            padx=20, pady=10,
            state=tk.DISABLED
        )
        self.l_button.pack(side=tk.LEFT, padx=10)
        self.s_button = tk.Button(
            button_frame,
            text="Second Greater",
            command=self.show_result,
            font=("Helvetica", 24),
            padx=20, pady=10,
            state=tk.DISABLED
        )
        self.s_button.pack(side=tk.LEFT, padx=10) 

        self.result_label = tk.Label(self.pre_trial_frame, text="", font=("Helvetica", 28))
        self.result_label.pack(pady=20)

        # 绑定空格键用于预实验阶段的刺激控制
        self.root.bind("<space>", self.handle_pre_trial_space)

        # ----- 试次（正式实验）页面 -----
        self.trial_label = tk.Label(
            self.trial_frame,
            font=("Helvetica", 24),
            wraplength=1000
        )
        self.trial_label.pack(pady=50)

        button_frame_trial = tk.Frame(self.trial_frame)
        button_frame_trial.pack(pady=20)
        self.option1_button = tk.Button(
            button_frame_trial,
            text="First Greater",
            font=("Helvetica", 24),
            width=12,
            height=2,
            command=lambda: self.handle_trial_response("First Greater"),
            state=tk.DISABLED
        )
        self.option1_button.pack(side=tk.LEFT, padx=10)
        self.option3_button = tk.Button(
            button_frame_trial,
            text="Second Greater",
            font=("Helvetica", 24),
            width=12,
            height=2,
            command=lambda: self.handle_trial_response("Second Greater"),
            state=tk.DISABLED
        )
        self.option3_button.pack(side=tk.LEFT, padx=10)

        # ----- 最终页面 -----
        self.final_label = tk.Label(
            self.final_frame,
            text="Thank you.",
            font=("Helvetica", 28),
            wraplength=1000
        )
        self.final_label.pack(pady=100)
        self.exit_button = tk.Button(
            self.final_frame,
            text="Exit",
            font=("Helvetica", 24),
            command=self.root.quit
        )
        self.exit_button.pack(pady=20)

    def start_experiment(self):
        self.main_frame.pack_forget()
        self.show_pre_trial_page()

    def show_pre_trial_page(self):
        self.main_frame.pack_forget()
        self.pre_trial_frame.pack(expand=True, fill='both')
        # 重置预试次阶段
        self.phase_stage = 0
        # 禁用预试次响应按钮，等待两次刺激完成
        self.l_button.config(state=tk.DISABLED)
        self.s_button.config(state=tk.DISABLED)
        self.pre_trial_label.config(
            text="This is a practice.\n\nPress SPACE to receive the first stimulation."
        )

    def handle_pre_trial_space(self, event):
        """
        预实验阶段使用空格键：
          - 第一次按下空格：触发第一个刺激，并更新提示
          - 第二次按下空格：触发第二个刺激，并启用响应按钮
        """
        if self.phase_stage == 0:
            self.pre_trial_label.config(
                text="First stimulation triggered.\n\nPress SPACE for the second stimulation."
            )
            self.trigger_pre_trial_move(0)
            self.phase_stage = 1 
        elif self.phase_stage == 1:
            self.pre_trial_label.config(
                text="Second stimulation triggered.\n\nNow please make your choice."
            )
            self.trigger_pre_trial_move(1)
            self.phase_stage = 2
            # 两次刺激完成后启用响应按钮
            self.l_button.config(state=tk.NORMAL)
            self.s_button.config(state=tk.NORMAL)

    def trigger_pre_trial_move(self, index):
        """
        根据预试次的索引触发相应的运动刺激。
        """
        if self.controller and index < len(self.pre_trial_move_value):
            move = self.pre_trial_move_value[index]
            self.controller.move_to_position(move)

    def show_result(self):
        """
        用户在预实验阶段点击选择按钮后：
          - 显示提示信息，告知预实验结束
          - 然后进入正式实验页面
        """
        self.result_label.pack(pady=20)
        self.result_label.config(
            text="Pre-experiment finished. Let's proceed to the formal experiment.",
            fg="black"
        )
        self.root.after(6000, self.goto_trial_page)

    def goto_trial_page(self):
        self.result_label.pack_forget()
        self.show_trial_page()

    def show_trial_page(self):
        # 移除预试次页面并设置试次页面
        self.pre_trial_frame.pack_forget()
        self.trial_frame.pack(expand=True, fill='both')
        # 为正式实验分配当前试次的运动对
        if self.trial_move_values and self.trial_count < len(self.trial_move_values):
            self.current_trial_pair = self.trial_move_values[self.trial_count]
        else:
            print("试次运动指令不足！")
            return

        # 重置试次阶段，初始禁用响应按钮
        self.phase_stage = 0
        self.option1_button.config(state=tk.DISABLED)
        self.option3_button.config(state=tk.DISABLED)
        self.root.bind("<space>", self.handle_trial_space)
        self.trial_label.config(
            text=f"Trial {self.trial_count + 1}: Press SPACE to receive the first stimulation."
        )

    def handle_trial_space(self, event):
        """
        正式实验阶段使用空格键：
          - 第一次按下空格：触发第一个刺激，并更新提示文本
          - 第二次按下空格：触发第二个刺激，并启用响应按钮
        """
        if self.phase_stage == 0:
            self.trial_label.config(
                text=f"Trial {self.trial_count + 1}: First stimulation triggered.\n\nPress SPACE for the second stimulation."
            )
            self.trigger_trial_move_phase(0)
            self.phase_stage = 1
        elif self.phase_stage == 1:
            self.trial_label.config(
                text=f"Trial {self.trial_count + 1}: Second stimulation triggered.\n\nNow please make your choice."
            )
            self.trigger_trial_move_phase(1)
            self.phase_stage = 2
            # 启用正式实验的响应按钮
            self.option1_button.config(state=tk.NORMAL)
            self.option3_button.config(state=tk.NORMAL)

    def trigger_trial_move_phase(self, index):
        """
        根据正式实验阶段的索引来触发相应的运动刺激。
        """
        if self.controller and self.current_trial_pair:
            if index < len(self.current_trial_pair):
                move = self.current_trial_pair[index]
                self.controller.move_to_position(move)
            else:
                print("运动指令不足！")

    def handle_trial_response(self, response):
        """
        用户在正式实验阶段点击选择按钮后：
          1. 记录结果
          2. 累加试次计数
          3. 解绑空格键
          4. 进入下一试次或结束实验
        """
        result = {
            "trial": self.trial_count + 1,
            "value": self.current_trial_pair,
            "response": response
        }
        self.responses.append(result)
        self.trial_count += 1
        self.trial_frame.pack_forget()
        self.root.unbind("<space>")
        if self.trial_count < self.MAX_TRIALS:
            self.show_trial_page()
        else:
            self.show_final_page()

    def show_final_page(self):
        self.final_frame.pack(expand=True, fill='both')


    def run(self):
        """
        复位操作, 启动UI主循环
        """
        if self.controller:
            current_pos = self.controller.read_current_position()
            self.controller.move_to_position([current_pos, 0])
        self.root.mainloop()


if __name__ == '__main__':
    dummy_controller = DummyController()

    pre_trial_move_value = [
        [[500, 0]],  # First stimulation
        [[100, 0]]   # Second stimulation
    ]

    pair_count = 2
    all_trials = get_trial_moves(pair_count)

    max_trial = len(all_trials)
    trial_move_values = all_trials

    ui = ExperimentUI(controller=dummy_controller, 
                      pre_trial_move_value=pre_trial_move_value, 
                      trial_move_values=trial_move_values,
                      max_trial=max_trial)
    ui.run()
