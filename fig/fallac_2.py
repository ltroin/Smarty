import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl


mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 24

updated_data = {
    "Model": [
        "DeepSeek V3", "Grok-2", "GPT-o3-mini", "Claude 3.7", "DeepSeek R1",
        "GPT-4o", "LLaMA 3.1", "Claude 3.5"
    ],
    "False Positive": [
        0.08333333333333333,  # DeepSeek V3
        0.11646586345381527,  # Grok-2
        0.17045454545454544,  # GPT-o3-mini
        0.2028985507246377,   # Claude 3.7
        0.24914675767918087,  # DeepSeek R1
        0.23875432525951557,  # GPT-4o
        0.2465753424657534,   # LLaMA 3.1
        0.24914675767918087   # Claude 3.5
    ],
    "False Negative": [
        0.0,                  # DeepSeek V3
        0.0,                  # Grok-2
        0.005681818181818182, # GPT-o3-mini
        0.0,                  # Claude 3.7
        0.0,                  # DeepSeek R1
        0.0,                  # GPT-4o
        0.0,                  # LLaMA 3.1
        0.0                   # Claude 3.5
    ],
    "F1": [
        0.957,  # DeepSeek V3
        0.938,  # Grok-2
        0.904,  # GPT-o3-mini
        0.887,  # Claude 3.7
        0.858,  # DeepSeek R1
        0.864,  # GPT-4o
        0.859,  # LLaMA 3.1
        0.858   # Claude 3.5
    ]
}


fresh_colors = np.array([
    "#5A7486",
    "#615C59",
    "#D88C85",
    "#B89254",
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
    "False Positive": (0, 0.5),
    "False Negative": (0, 0.01),
    "F1": (0, 1)
}


fig, axes = plt.subplots(1, 3, figsize=(24, 8))

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
fig.savefig("F1_line_2_2.pdf", format="pdf")
