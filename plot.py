import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def logistic(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

with open('kai_6min_results.txt', 'r') as file:
    lines = file.readlines()

data = []
standard_mm = 5.5

for line in lines:
    try:
        _, rest = line.split(":", 1)
        rest = rest.strip()
        left_str, right_str = rest.split(" vs ", 1)
        left_mm = float(left_str.replace("mm", "").strip())
        tokens = right_str.split()
        right_mm = float(tokens[0].replace("mm", "").strip())
        response = " ".join(tokens[1:])
    except Exception as e:
        continue
    
    if left_mm == standard_mm and right_mm == standard_mm:
        candidate_mm = standard_mm
        y = 0.5
    else:
        if left_mm != standard_mm:
            candidate_mm = left_mm
            candidate_position = "left"
        else:
            candidate_mm = right_mm
            candidate_position = "right"
        
        if response == "First Greater":
            y = 1.0 if candidate_position == "left" else 0.0
        elif response == "Second Greater":
            y = 1.0 if candidate_position == "right" else 0.0
        else:
            continue

    data.append((candidate_mm, y))

df = pd.DataFrame(data, columns=['x', 'y'])

# 对相同刺激数值的试验求平均响应
grouped = df.groupby('x').mean().reset_index()
x_data = grouped['x'].values
y_data = grouped['y'].values

# 初始猜测参数：最大值L、斜率k和PSE (x0)
p0 = [1, 1, 5]

params, _ = curve_fit(logistic, x_data, y_data, p0)
L, k, x0 = params
pse = x0

x_smooth = np.linspace(min(x_data), max(x_data), 200)
y_smooth = logistic(x_smooth, *params)

plt.figure(figsize=(10, 6))
plt.scatter(x_data, y_data, s=50, color='navy', zorder=5, label='Mean proportion')
plt.plot(x_smooth, y_smooth, color='red', linewidth=2, label='Logistic fit')
plt.axhline(0.5, color='green', linestyle=':', linewidth=1.5, label='50% threshold')
plt.axvline(standard_mm, color='orange', linestyle='--', linewidth=1, alpha=0.5, label=f'Standard ({standard_mm}mm)')

plt.text(pse + 0.2, 0.53, f'PSE = {pse:.1f}mm', color='black', ha='left', va='center', fontsize=12)
plt.xlabel('Comparison Stimulus Length (mm)', fontsize=12)
plt.ylabel('Proportion', fontsize=12)
plt.title('PSE Estimation', fontsize=14)
plt.ylim(0, 1)
plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.show()
