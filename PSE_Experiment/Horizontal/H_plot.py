import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def load_and_parse_abs(filename):
    """
    Read and parse depth_result.txt.
    For each mm value, strip extra spaces, convert to float,
    take the absolute value, and record its trial stage.
    """
    rows = []
    current_stage = None
    pattern = re.compile(
        r"Trial\s+(\d+):\s+(-?[\d\s]+\.\d+)mm\s+vs\s+(-?[\d\s]+\.\d+)mm\s+(First Greater|Second Greater)"
    )
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("==="):
                if "Left" in line:
                    current_stage = "left"
                elif "Right" in line:
                    current_stage = "right"
                continue

            m = pattern.match(line)
            if not m:
                continue

            trial, mm1_str, mm2_str, resp_str = m.groups()
            mm1 = abs(float(mm1_str.replace(" ", "")))
            mm2 = abs(float(mm2_str.replace(" ", "")))

            rows.append({
                'stage':    current_stage,
                'trial':    int(trial),
                'mm1':      mm1,
                'mm2':      mm2,
                'resp_str': resp_str
            })

    return pd.DataFrame(rows)


def count_mixed_logic_abs(df, std_value=5.5):
    """
    For any trial where either mm1 or mm2 equals std_value (absolute),
    exclude trials where both equal std_value.
    Then:
      - if test > std_value: count “correct” responses
      - if test < std_value: count “incorrect” responses
    Returns:
      test_values: sorted array of test stimulus levels
      counts: 2×N array where
        counts[0, i] = total trial count at test_values[i]
        counts[1, i] = accumulated correct/incorrect count
    """
    mask_std = (df['mm1'] == std_value) | (df['mm2'] == std_value)
    df_std = df[mask_std & ~((df['mm1'] == std_value) & (df['mm2'] == std_value))].copy()

    tests = np.where(df_std['mm1'] == std_value, df_std['mm2'], df_std['mm1'])
    test_values = np.sort(np.unique(tests))

    counts = np.zeros((2, len(test_values)), dtype=int)
    index_map = {val: i for i, val in enumerate(test_values)}

    for _, row in df_std.iterrows():
        mm1, mm2, resp = row['mm1'], row['mm2'], row['resp_str']
        test = mm2 if mm1 == std_value else mm1
        idx = index_map[test]
        counts[0, idx] += 1

        correct = (
            (resp == "First Greater"  and mm1 > mm2) or
            (resp == "Second Greater" and mm2 > mm1)
        )

        if test > std_value:
            if correct:
                counts[1, idx] += 1
        else:
            if not correct:
                counts[1, idx] += 1

    return test_values, counts


def logistic(x, x0, k):
    """Standard logistic psychometric function."""
    return 1.0 / (1.0 + np.exp(-k * (x - x0)))

##################
# Main loop
if __name__ == "__main__":
    filepath = os.path.join("Results", "Kevin_H.txt")
    df = load_and_parse_abs(filepath)

    for label, subset in [
        ("Left only",  df[df['stage'] == "left"]),
        ("Right only", df[df['stage'] == "right"]),
        ("Combined",      df)
    ]:
        # Compute counts and rates
        x, counts = count_mixed_logic_abs(subset, std_value=5.5)
        y = counts[1] / counts[0]

        # Print summary arrays
        print(f"\n--- {label} ---")
        print("Test stimuli (mm, absolute):      ", x)
        print("Total trial counts:               ", counts[0])
        print(">5.5 correct / <5.5 incorrect:    ", counts[1])
        print("Response rates:                   ", np.round(y, 3))

        # Fit logistic
        initial_guess = [5.5, 1.0]
        popt, _ = curve_fit(
            logistic, x, y,
            p0=initial_guess,
            bounds=([0, 0], [np.inf, np.inf])
        )
        x0, k = popt
        print(f"Threshold (50% point) x₀ = {x0:.3f} mm, slope k = {k:.3f}")

        # Plot
        plt.figure()
        plt.scatter(x, y, label="Data")
        x_fit = np.linspace(4.5, 6.5, 200)
        y_fit = logistic(x_fit, *popt)
        plt.plot(x_fit, y_fit, '-', label="Logistic fit")
        plt.axhline(0.5, color='gray', linestyle='--')
        plt.axvline(x0, color='red', linestyle='--',
                    label=f"50% at {x0:.2f} mm")
        plt.xlabel('Test stimulus (mm)')
        plt.ylabel('Response rate')
        plt.title(label)
        plt.legend()
        plt.xlim(4.5, 6.5)
        plt.ylim(0, 1)
        plt.xticks(np.arange(4.5, 6.6, 0.2))
        plt.yticks(np.arange(0.0, 1.01, 0.2))

        plt.tight_layout()
        plt.show()
