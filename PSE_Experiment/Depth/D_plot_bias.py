import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def load_and_parse_abs(filename):
    rows = []
    current_stage = None
    pattern = re.compile(
        r"Trial\s+(\d+):\s+(-?[\d\s]+\.\d+)mm\s+vs\s+(-?[\d\s]+\.\d+)mm\s+([12])\s+(First Greater|Second Greater)"
    )
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("==="):
                if "Forward" in line:
                    current_stage = "forward"
                elif "Backward" in line:
                    current_stage = "backward"
                continue
            m = pattern.match(line)
            if not m:
                continue
            trial, mm1_str, mm2_str, std_idx, resp_str = m.groups()
            mm1 = abs(float(mm1_str.replace(" ", "")))
            mm2 = abs(float(mm2_str.replace(" ", "")))
            rows.append({
                'stage':    current_stage,
                'trial':    int(trial),
                'mm1':      mm1,
                'mm2':      mm2,
                'std_idx':  int(std_idx),
                'resp_str': resp_str
            })
    return pd.DataFrame(rows)

def estimate_response_bias(df):
    """
    Compute response bias = P(test > standard | equal stimuli),
    correctly accounting for std_idx.
    """
    eq = df[df['mm1'] == df['mm2']]
    if eq.empty:
        return 0.0
    is_test_greater = (
        (eq['std_idx'] == 1) & (eq['resp_str'] == "Second Greater")
    ) | (
        (eq['std_idx'] == 2) & (eq['resp_str'] == "First Greater")
    )
    return is_test_greater.mean()

def count_mixed_logic_abs(df, std_value=5.5):
    mask_std = (df['mm1'] == std_value) | (df['mm2'] == std_value)
    df_std = df[mask_std & ~((df['mm1']==std_value)&(df['mm2']==std_value))].copy()
    tests = np.where(df_std['mm1']==std_value, df_std['mm2'], df_std['mm1'])
    test_values = np.sort(np.unique(tests))
    counts = np.zeros((2, len(test_values)), dtype=int)
    idx_map = {v:i for i,v in enumerate(test_values)}
    for _, row in df_std.iterrows():
        mm1, mm2, resp = row['mm1'], row['mm2'], row['resp_str']
        test = mm2 if mm1==std_value else mm1
        idx = idx_map[test]
        counts[0, idx] += 1
        correct = (
            (resp=="First Greater"  and mm1>mm2) or
            (resp=="Second Greater" and mm2>mm1)
        )
        if test>std_value:
            if correct:
                counts[1, idx] += 1
        else:
            if not correct:
                counts[1, idx] += 1
    return test_values, counts

def logistic(x, x0, k):
    return 1.0 / (1.0 + np.exp(-k*(x-x0)))

if __name__ == "__main__":
    filepath = os.path.join("Results", "Will_D.txt")
    df = load_and_parse_abs(filepath)

    # 3 stage
    subsets = {
        "Forward only":  df[df['stage']=="forward"],
        "Backward only": df[df['stage']=="backward"],
        "Combined":      df
    }

    # 1) bias γ
    gammas = {}
    for label, sub in subsets.items():
        g = estimate_response_bias(sub)
        gammas[label] = g
        print(f"Response bias γ for {label}: {g:.3f}")

    # 2) draw
    for label, sub in subsets.items():
        gamma = gammas[label]

        # 2a) Orig PSE
        x, counts = count_mixed_logic_abs(sub, std_value=5.5)
        y_orig = counts[1] / counts[0]

        # 2b) corrected PSE
        denom = 1 - 2*gamma
        if abs(denom) < 1e-8:
            y_corr = y_orig.copy()
        else:
            y_corr = (y_orig - gamma) / denom
            y_corr = np.clip(y_corr, 0, 1)

        mask = np.isfinite(y_corr)
        x_fit, y_fit = x[mask], y_corr[mask]
        p0 = [5.5, 1.0]
        popt_o, _ = curve_fit(logistic, x, y_orig, p0=p0, bounds=([0,0],[np.inf,np.inf]))
        popt_c, _ = curve_fit(logistic, x_fit, y_fit, p0=p0, bounds=([0,0],[np.inf,np.inf]))
        x0_o, k_o = popt_o
        x0_c, k_c = popt_c

        print(f"\n--- {label} ---")
        print(f" Orig PSE x₀={x0_o:.3f}, corrected PSE x₀={x0_c:.3f}")

        # 2d) draw
        plt.figure()
        plt.scatter(x, y_orig, label='Data (orig)', alpha=0.6)
        plt.scatter(x, y_corr, label='Data (corr)', alpha=0.6, marker='s')
        xf = np.linspace(x.min(), x.max(), 200)
        plt.plot(xf, logistic(xf,*popt_o), '-', label='Fit (orig)')
        plt.plot(xf, logistic(xf,*popt_c), '--', label='Fit (corr)')
        plt.axhline(gammas[label], color='gray', linestyle=':', label=f'γ={gammas[label]:.2f}')
        plt.axhline(1-gammas[label], color='gray', linestyle=':', label=f'1-γ={1-gammas[label]:.2f}')
        plt.axhline(0.5, color='black', linestyle='--')
        plt.xlabel('Test stimulus (mm)')
        plt.ylabel('Response rate')
        plt.title(f"{label}")
        plt.legend()
        plt.tight_layout()
        plt.show()
