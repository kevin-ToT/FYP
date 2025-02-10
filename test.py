import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Data setup
data = [
    {"Out Date": "2017-09-10", "In Date": None},
    {"Out Date": "2018-07-08", "In Date": "2018-08-07"},
    {"Out Date": "2018-12-15", "In Date": "2019-01-04"},
    {"Out Date": "2019-06-16", "In Date": "2019-08-03"},
    {"Out Date": "2020-03-20", "In Date": "2020-09-03"},
    {"Out Date": "2021-05-25", "In Date": "2021-10-14"},
    {"Out Date": "2023-12-16", "In Date": "2024-01-08"},
    {"Out Date": "2024-01-25", "In Date": "2024-01-28"},
    {"Out Date": "2024-04-02", "In Date": "2024-04-08"},
    {"Out Date": "2024-06-08", "In Date": "2024-06-12"},
    {"Out Date": "2024-09-06", "In Date": "2024-10-05"},
    {"Out Date": "27/12/2024", "In Date": "08/01/2025"},
    {"Out Date": "13/08/2027", "In Date": "10/09/2027"}
]

# Convert data to DataFrame
df = pd.DataFrame(data)

# Convert date strings to datetime
for col in ['Out Date', 'In Date']:
    df[col] = pd.to_datetime(df[col], format='%Y-%m-%d', errors='coerce')
    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce').combine_first(df[col])

# Plotting
plt.figure(figsize=(12, 6))

# Plot out and in dates
for idx, row in df.iterrows():
    if pd.notna(row['In Date']):
        plt.plot([row['Out Date'], row['In Date']], [idx, idx], color='blue', linewidth=2, marker='o')
    else:
        plt.scatter(row['Out Date'], idx, color='red', label='No In Date' if idx == 0 else "")

plt.title('Out and In Dates Timeline')
plt.xlabel('Date')
plt.ylabel('Event Index')
plt.yticks(range(len(df)), [f'Event {i+1}' for i in range(len(df))])
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()