def raw_to_mm(raw: int, min_movement=322, step_size=14) -> float:
    """
    将 raw 数值转换为毫米数。
    """
    return (raw - min_movement) / step_size + 4.6

def generate_result_file(responses, filename="results.txt", step_size=14, min_movement=322):
    """
    生成结果文件，每一行转换为 mm vs mm 格式。
    示例行：
      Trial 1: 5.4mm vs 5.0mm First Greater
    """
    with open(filename, "w", encoding="utf-8") as f:
        for res in responses:
            trial = res["trial"]
            pair = res["value"]  # 格式为 [[raw1, 0], [raw2, 0]]
            response = res["response"]
            mm_values = []
            for move in pair:
                raw = move[0]
                mm = raw_to_mm(raw, min_movement, step_size)
                mm_values.append(round(mm, 1))
            f.write(f"Trial {trial}: {mm_values[0]}mm vs {mm_values[1]}mm {response}\n")
    print(f"Results saved to {filename}")
