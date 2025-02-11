import tkinter as tk

repeat_count = 0  # 用于计数第三页的次数
MAX_REPEATS = 20  # 设置最大重复次数

def show_second_page():
    main_frame.pack_forget()
    second_frame.pack(expand=True, fill='both')

def show_result(is_correct):
    result_label.pack(pady=50)
    if is_correct:
        result_label.config(text="Correct!", fg="green")
    else:
        result_label.config(text="Incorrect!", fg="red")
    # 2秒后进入第三页
    root.after(2000, show_third_page)

def show_third_page():
    second_frame.pack_forget()
    third_frame.pack(expand=True, fill='both')
    update_third_page()

def update_third_page():
    global repeat_count
    if repeat_count < MAX_REPEATS:
        question_label_third.config(text=f"Trial {repeat_count + 1}: Please compare the first movement with the second movement.")
        repeat_count += 1
        root.after(2000)
    else:
        show_final_page()

def show_final_page():
    third_frame.pack_forget()
    final_frame.pack(expand=True, fill='both')

def handle_third_page_response(response):
    print(f"Response for trial {repeat_count}: {response}")
    update_third_page()

# 创建主窗口
root = tk.Tk()
root.title("Interactive UI")
root.geometry("1600x1000")

# 主界面容器
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill='both')

welcome_label = tk.Label(main_frame, text="Welcome! Click Start to begin.", font=("Helvetica", 32))
welcome_label.pack(pady=(200, 50))

start_button = tk.Button(main_frame, text="Start the Experiment", command=show_second_page, font=("Helvetica", 28), padx=30, pady=20)
start_button.pack()

# 第二页容器
second_frame = tk.Frame(root)

question_label_second = tk.Label(second_frame, text="Please feel the movement and compare the first movement with the second movement", font=("Helvetica", 32))
question_label_second.pack(pady=100)

button_frame_second = tk.Frame(second_frame)
button_frame_second.pack()

big_button = tk.Button(button_frame_second, text="Larger", font=("Helvetica", 28), command=lambda: show_result(True), width=8, height=2)
big_button.pack(side=tk.LEFT, padx=50)

small_button = tk.Button(button_frame_second, text="Smaller", font=("Helvetica", 28), command=lambda: show_result(False), width=8, height=2)
small_button.pack(side=tk.RIGHT, padx=50)

result_label = tk.Label(second_frame, text="", font=("Helvetica", 32))

# 第三页容器
third_frame = tk.Frame(root)

question_label_third = tk.Label(third_frame, text="", font=("Helvetica", 32))
question_label_third.pack(pady=100)

button_frame_third = tk.Frame(third_frame)
button_frame_third.pack()

big_button_third = tk.Button(button_frame_third, text="First Greater", font=("Helvetica", 28), width=12, height=2, command=lambda: handle_third_page_response("First Greater"))
big_button_third.pack(side=tk.LEFT, padx=20)

equal_button_third = tk.Button(button_frame_third, text="=", font=("Helvetica", 28), width=12, height=2, command=lambda: handle_third_page_response("Equal"))
equal_button_third.pack(side=tk.LEFT, padx=20)

small_button_third = tk.Button(button_frame_third, text="First Smaller", font=("Helvetica", 28), width=12, height=2, command=lambda: handle_third_page_response("First Smaller"))
small_button_third.pack(side=tk.LEFT, padx=20)

# 最终页面容器
final_frame = tk.Frame(root)

final_label = tk.Label(final_frame, text="Experiment Completed! Thank you for participating.", font=("Helvetica", 32))
final_label.pack(pady=200)

finish_button = tk.Button(final_frame, text="Exit", font=("Helvetica", 28), command=root.quit)
finish_button.pack(pady=50)

root.mainloop()
