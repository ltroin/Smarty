import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 16

fallacy_scores = {
    "Grok-2": -52.558,
    "DeepSeek R1": -97.979,
    "DeepSeek V3": -151.259,
    "Claude 3.7": -242.337,
    "Claude 3.7 Ex": -200.937,
    "Claude 3.5": -248.949,
    "GPT-4o": -246.071,
    "GPT-o3-mini": -255.588,
    "LLaMA 3.1": -257.261
}


sorted_items = sorted(fallacy_scores.items(), key=lambda x: x[1], reverse=True)
models_fallacy, scores = zip(*sorted_items)
models_fallacy = list(models_fallacy)
scores = list(scores)

fresh_colors = np.array([
    "#5A7486",
    "#615C59",
    "#D88C85",
    "#B89254",
    "#8EC1CD",
    "#A96363",
    "#B9AA9A",
    "#D9BF94",
    "#A1763A"
])


color_map = {
    "DeepSeek V3": fresh_colors[0],
    "Grok-2": fresh_colors[1],
    "GPT-o3-mini": fresh_colors[2],
    "Claude 3.7": fresh_colors[3],
    "DeepSeek R1": fresh_colors[4],
    "GPT-4o": fresh_colors[5],
    "LLaMA 3.1": fresh_colors[6],
    "Claude 3.5": fresh_colors[7],
    "Claude 3.7 Ex": fresh_colors[8],
}


bar_colors = [color_map[model] for model in models_fallacy]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(models_fallacy, scores, color=bar_colors)

ax.set_xlim(0, -300)
ax.set_title("Comparison of Fallacy Label Score (Higher is Better)")
ax.set_xlabel("Score")
ax.invert_yaxis()

ax.grid(axis='x', linestyle='--', linewidth=0.7)
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 28,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f}",
            va='center',
            ha='left',
            color='white')
plt.tight_layout()
plt.show()

fig.savefig("fallacy_line.pdf", format="pdf")
