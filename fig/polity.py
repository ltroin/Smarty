import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl


mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 24

updated_data = {
    "Model": [
        "DeepSeek V3", "Grok-2", "GPT-o3-mini", "Claude 3.7", "Claude 3.7 Ex", "DeepSeek R1",
        "GPT-4o", "LLaMA 3.1", "Claude 3.5"
    ],
        "False Positive": [
        0.1166077738515901,      # DeepSeek V3
        0.13793103448275862,     # Grok-2
        0.19063004846526657,     # GPT-o3-mini
        0.21962616822429906,     # Claude 3.7 Sonnet
        0.23860182370820668,     # Claude 3.7 Sonnet Thinking (Ex)
        0.24962406015037594,     # DeepSeek R1
        0.24511278195488723,     # GPT-4o
        0.26392961876832843,     # LLaMA 3.1 405b
        0.2606774668630339       # Claude 3.5
    ],
    "False Negative": [
        0.00904977375565611,     # DeepSeek V3
        0.009345794392523364,    # Grok-2
        0.007712082262210797,    # GPT-o3-mini
        0.00819672131147541,     # Claude 3.7 Sonnet
        0.002890173410404624,    # Claude 3.7 Sonnet Thinking (Ex)
        0.014577259475218658,    # DeepSeek R1
        0.0058309037900874635,   # GPT-4o
        0.006134969325153374,    # LLaMA 3.1 405b
        0.0060790273556231       # Claude 3.5
    ],
    "F1": [
        0.934,                   # DeepSeek V3
        0.921,                   # Grok-2
        0.891,                   # GPT-o3-mini
        0.873,                   # Claude 3.7 Sonnet
        0.863,                   # Claude 3.7 Sonnet Thinking (Ex)
        0.85,                    # DeepSeek R1
        0.857,                   # GPT-4o
        0.845,                   # LLaMA 3.1 405b
        0.847                    # Claude 3.5
    ]
}

fresh_colors = np.array([
    "#5A7486",
    "#615C59",
    "#D88C85",
    "#B89254",
    "#A1763A",
    "#8EC1CD",
    "#A96363",
    "#B9AA9A",
    "#D9BF94"
])


values_updated = np.array([
    updated_data["False Positive"],
    updated_data["False Negative"],
    updated_data["F1"]
])


metrics = ["False Positive", "False Negative", "F1"]
models = updated_data["Model"]

y_limits = {
    "False Positive": (0, 0.3),
    "False Negative": (0, 0.3),
    "F1": (0, 1)
}


fig, axes = plt.subplots(1, 3, figsize=(30, 8))

# for i, metric in enumerate(metrics):
#     # ax = axes[i]
#     axes[i].bar(models, values_updated[i], color=fresh_colors, alpha=0.8)
#     axes[i].set_title(metric)
#     axes[i].set_xticks(np.arange(len(models)))
#     axes[i].set_xticklabels(models, rotation=45, ha="right")
#     axes[i].set_ylabel("Score")
#     axes[i].set_ylim(y_limits[metric])
#     axes[i].grid(True, axis='y', linestyle='--', alpha=0.5)
#     axes[i].grid(True, axis='x', linestyle='--', alpha=0.5)
#     # mean_value = np.mean(values_updated[i])
#     # ax.axhline(mean_value, color='gray', linestyle='--', linewidth=1)
#     # ax.text(len(models)-0.5, mean_value + 0.01, f"Avg: {mean_value:.3f}", color='gray', fontsize=9)

for i, metric in enumerate(metrics):

    bars = axes[i].bar(models, values_updated[i], color=fresh_colors, alpha=0.8)
    axes[i].set_title(metric)
    axes[i].set_xticks(np.arange(len(models)))
    axes[i].set_xticklabels(models, rotation=45, ha="right")
    axes[i].set_ylabel("Score")
    axes[i].set_ylim(y_limits[metric])
    axes[i].grid(True, axis='y', linestyle='--', alpha=0.5)
    axes[i].grid(True, axis='x', linestyle='--', alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        axes[i].text(bar.get_x() + bar.get_width() / 2, height, f'{height:.3f}',
                     ha='center', va='bottom', fontsize=22)

plt.tight_layout()
plt.show()
fig.savefig("F1_line.pdf", format="pdf")
