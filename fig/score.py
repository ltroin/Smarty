import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

custom_font = font_manager.FontProperties(family='Times New Roman', size=18)

data = [
    ['accident fallacy', 'Direct', 0, 3, 35, 22],
    ['accident fallacy', 'Prolog', 0, 1, 29, 30],
    ['accident fallacy', 'ExpertProlog', 0, 0, 0, 60],
    ['contextomy', 'Direct', 0, 0, 44, 16],
    ['contextomy', 'Prolog', 0, 2, 40, 18],
    ['contextomy', 'ExpertProlog', 0, 0, 5, 55],
    ['inverse error', 'Direct', 5, 12, 34, 9],
    ['inverse error', 'Prolog', 0, 14, 39, 7],
    ['inverse error', 'ExpertProlog', 0, 0, 10, 50],
    ['false premise', 'Direct', 0, 0, 24, 36],
    ['false premise', 'Prolog', 0, 0, 22, 38],
    ['false premise', 'ExpertProlog', 0, 0, 0, 60],
    ['false analogy', 'Direct', 0, 7, 32, 21],
    ['false analogy', 'Prolog', 0, 1, 21, 38],
    ['false analogy', 'ExpertProlog', 0, 0, 0, 60],
    ['wrong direction', 'Direct', 0, 6, 28, 26],
    ['wrong direction', 'Prolog', 0, 5, 32, 23],
    ['wrong direction', 'ExpertProlog', 0, 0, 0, 60],
    ['fallacy of composition', 'Direct', 0, 11, 40, 9],
    ['fallacy of composition', 'Prolog', 0, 0, 35, 25],
    ['fallacy of composition', 'ExpertProlog', 0, 0, 0, 60],
    ['begging the question', 'Direct', 0, 8, 38, 14],
    ['begging the question', 'Prolog', 0, 0, 33, 27],
    ['begging the question', 'ExpertProlog', 0, 0, 2, 58],
    ['false cause', 'Direct', 0, 5, 48, 7],
    ['false cause', 'Prolog', 0, 1, 38, 21],
    ['false cause', 'ExpertProlog', 0, 0, 3, 57],
    ['improper transposition', 'Direct', 8, 9, 27, 16],
    ['improper transposition', 'Prolog', 3, 3, 37, 17],
    ['improper transposition', 'ExpertProlog', 0, 0, 0, 60],
    ['improper distribution or addition', 'Direct', 0, 6, 32, 22],
    ['improper distribution or addition', 'Prolog', 0, 3, 37, 20],
    ['improper distribution or addition', 'ExpertProlog', 0, 0, 6, 54],
]


df = pd.DataFrame(data, columns=['Fallacy', 'Method', '0', '1', '2', '3'])

method_names = {
    'Direct': 'Direct',
    'Prolog': 'Prolog',
    'ExpertProlog': 'Expert',
}


fallacy_short_map = {
    'accident fallacy': 'AF',
    'contextomy': 'CT',
    'inverse error': 'IE',
    'false premise': 'FP',
    'false analogy': 'FA',
    'wrong direction': 'WD',
    'fallacy of composition': 'FC',
    'begging the question': 'BQ',
    'false cause': 'FS',
    'improper transposition': 'IT',
    'improper distribution or addition': 'ID'
}


df['FallacyShort'] = df['Fallacy'].map(fallacy_short_map)


fallacies = df['FallacyShort'].unique()
methods = ['Direct', 'Prolog', 'ExpertProlog']
scores = ['0', '1', '2', '3']


method_colors = {
    'Direct': ['#E7F1FA', '#A9C9E5', '#5A9ACF', '#2D5F91'],
    'Prolog': ['#F1F1F1', '#B4B4B4', '#6B6B6B', '#2E2E2E'],
    'ExpertProlog': ['#FCEEEF', '#F4B9BC', '#D77478', '#A13F3F']
}



fig, ax = plt.subplots(figsize=(16, 8))
bar_width = 0.22
x = np.arange(len(fallacies))


bottoms = {method: np.zeros(len(fallacies)) for method in methods}


for i, score in enumerate(scores):
    for j, method in enumerate(methods):
        method_data = df[df['Method'] == method][score].values
        xpos = x + (j - 1) * bar_width
        ax.bar(xpos, method_data, bar_width,
               bottom=bottoms[method],
               color=method_colors[method][i],
               edgecolor='white')
        bottoms[method] += method_data


import matplotlib.patches as mpatches
legend_patches = []
for method in methods:
    for i, score in enumerate(scores):
        custom_label = f"{method_names[method]} - {score}"
        patch = mpatches.Patch(color=method_colors[method][i], label=custom_label)
        legend_patches.append(patch)

ax.set_ylim(0, 60)
ax.yaxis.grid(True, linestyle='--', alpha=0.5)
ax.legend(
    handles=legend_patches,
    title='Method and Score',
    title_fontproperties=custom_font,
    prop=custom_font,
    bbox_to_anchor=(1.02, 1),
    loc='upper left'
)
ax.set_xticks(x)
ax.set_xticklabels(fallacies, rotation=45, fontproperties=custom_font)
ax.tick_params(axis='y', labelsize=16  )
ax.set_title('Stacked Bar Chart by Fallacy',
             fontproperties=custom_font)
ax.set_ylabel('Number of Scores', fontproperties=custom_font)
plt.tight_layout()
plt.show()
fig.savefig("score.pdf", format="pdf")