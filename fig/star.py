import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl


mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 8


updated_data = {
    "Model": [
        "DeepSeek V3", "Grok-2", "GPT-o3-mini", "Claude 3.7", "DeepSeek R1",
        "GPT-4o", "LLaMA 3.1", "Claude 3.5"
    ],
    "FP": [
        0.1166077738515901,
        0.13793103448275862,
        0.19063004846526657,
        0.21962616822429906,
        0.24962406015037594,
        0.24511278195488723,
        0.26392961876832843,
        0.2606774668630339
    ],
    "FN": [
        0.00904977375565611,
        0.009345794392523364,
        0.007712082262210797,
        0.00819672131147541,
        0.014577259475218658,
        0.0058309037900874635,
        0.006134969325153374,
        0.0060790273556231
    ],
    "F1": [
        0.934,
        0.921,
        0.891,
        0.873,
        0.85,
        0.857,
        0.845,
        0.847
    ]
}

fresh_colors = np.array([
    "#B2DFDB", "#F1F8E9", "#FFF9C4", "#FFE0B2",
    "#FFCCBC", "#D1C4E9", "#B3E5FC", "#C8E6C9"
])


metrics = ["FP", "FN", "F1"]
max_vals = {
    "FP": 0.3,
    "FN": 0.02,
    "F1": 1.0
}
models = updated_data["Model"]

num_metrics = len(metrics)

angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False)
angles = np.concatenate((angles, [angles[0]]))


normalized_data = []
for i in range(len(models)):
    vals = []
    for metric in metrics:
        norm_val = updated_data[metric][i] / max_vals[metric]
        vals.append(norm_val)
    vals.append(vals[0])
    normalized_data.append(vals)


fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))

ax.set_ylim(0, 1)

for idx, model in enumerate(models):
    ax.plot(angles, normalized_data[idx], label=model, color=fresh_colors[idx], marker='o')
    ax.fill(angles, normalized_data[idx], color=fresh_colors[idx], alpha=0.25)

ax.set_theta_offset(np.pi/2)
ax.set_theta_direction(-1)
ax.set_thetagrids(angles[:-1]*180/np.pi, metrics)

ax.set_yticklabels([])

ticks = np.linspace(0.2, 1.0, 5)
offset = -0.05

for i, metric in enumerate(metrics):
    theta = angles[i]
    for t in ticks:
        actual_val = t * max_vals[metric]
        ax.text(theta, t + offset, f"{actual_val:.2f}", color='gray', fontsize=9,
                horizontalalignment='center', verticalalignment='bottom')

plt.legend(loc='center left', bbox_to_anchor=(1.01, 0.5))

plt.title("Score for selected LLMs")
plt.tight_layout()
plt.show()
fig.savefig("F1.pdf", format="pdf", bbox_inches='tight', pad_inches=0.1)