import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
with open('results.txt', 'r') as file:
    lines = file.readlines()

data = []
standard_mm = 5

for line in lines:
    _, rest = line.split(":", 1)
    rest = rest.strip()
    left_str, right_str = rest.split(" vs ", 1)
    left_mm = int(left_str.replace("mm", "").strip())
    tokens = right_str.split()
    right_mm = int(tokens[0].replace("mm", "").strip())
    response = " ".join(tokens[1:])
    
    # 确定候选刺激位置
    if left_mm != standard_mm:
        candidate_mm = left_mm
        candidate_position = "left"
    else:
        candidate_mm = right_mm
        candidate_position = "right"
    
    # 编码响应值
    if response == "First Greater":
        if candidate_position == "left":
            y = 1.0   # 候选在左侧且被试认为"更大"
        else:
            y = 0.0   # 候选在右侧且被试认为左侧标准更大 → 候选更小
    elif response == "First Smaller":
        if candidate_position == "left":
            y = 0.0   # 候选在左侧且被试认为"更小"
        else:
            y = 1.0   # 候选在右侧且被试认为左侧标准更小 → 候选更大
    
    data.append((candidate_mm, y))

df = pd.DataFrame(data, columns=['x', 'y'])

# 每个刺激的平均概率
grouped = df.groupby('x').mean().reset_index()

x_group = grouped['x']
y_group = grouped['y']

import seaborn as sns
sns.regplot(x='x', y='y', data=grouped, lowess=True, scatter_kws={'s': 30})
plt.xlabel('x')
plt.ylabel('y')
plt.title('LOWESS')
plt.show()
