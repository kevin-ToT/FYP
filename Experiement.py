import tkinter as tk

def show_second_page():
    # 隐藏主界面组件
    main_frame.pack_forget()
    # 显示第二页
    second_frame.pack(expand=True, fill='both')

def show_result(is_correct):
    # 清除按钮
    big_button.pack_forget()
    small_button.pack_forget()
    # 显示结果
    if is_correct:
        result_label.config(text="正确！", fg="green")
    else:
        result_label.config(text="错误！", fg="red")
    result_label.pack(pady=50)

# 创建主窗口
root = tk.Tk()
root.title("Interactive UI")
root.geometry("1200x1000")

# 主界面容器
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill='both')

# 欢迎标签
welcome_label = tk.Label(
    main_frame,
    text="Welcome! Click Start to begin.",
    font=("Helvetica", 32)
)
welcome_label.pack(pady=(200, 50))

# 开始按钮
start_button = tk.Button(
    main_frame,
    text="Start the Experiment",
    command=show_second_page,
    font=("Helvetica", 28),
    padx=30,
    pady=20
)
start_button.pack()

# 第二页容器
second_frame = tk.Frame(root)

# 问题标签
question_label = tk.Label(
    second_frame,
    text="Please feel the movement and compare the first movemnet with second movent",
    font=("Helvetica", 32)
)
question_label.pack(pady=100)

# 按钮容器（用于水平排列按钮）
button_frame = tk.Frame(second_frame)
button_frame.pack()

# 大按钮
big_button = tk.Button(
    button_frame,
    text="Larger",
    font=("Helvetica", 28),
    command=lambda: show_result(True),
    width=8,
    height=2
)
big_button.pack(side=tk.LEFT, padx=50)

# 小按钮
small_button = tk.Button(
    button_frame,
    text="Smaller",
    font=("Helvetica", 28),
    command=lambda: show_result(False),
    width=8,
    height=2
)
small_button.pack(side=tk.RIGHT, padx=50)

# 结果标签
result_label = tk.Label(
    second_frame,
    text="",
    font=("Helvetica", 32)
)

root.mainloop()