import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations
import csv
import re
# Load the dataset from the provided CSV file
file_path = "ruozhiba_label.csv"

def format_sentence(sentence):

    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")

    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)

def clean_value(value):
    """Remove surrounding double quotes if present and strip whitespace."""
    if value.startswith("\"\"") and value.endswith("\"\""):
        value = value[1:-1].strip()
    value = value.replace("’", "'").replace("`", "'")
    return value

def convert_inner_quotes(text):
    """Convert inner double quotes to single quotes, keeping outer quotes unchanged."""
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", text)

# Read the CSV file
data = []
with open(file_path, 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        sentence = clean_value(row[0].strip())
        sentence = convert_inner_quotes(sentence)
        fallacy_type = row[11].strip().strip('"')
        fallacy_list = [f.strip().lower() for f in fallacy_type.split(',') if f.strip()]
        data.append((sentence, fallacy_list))

# Convert data into a DataFrame
df = pd.DataFrame(data, columns=['sentence', 'labels'])

# 1. Calculate average sentence length and standard deviation
df['sentence_length'] = df['sentence'].apply(lambda x: len(x.split()))
avg_length = df['sentence_length'].mean()
std_length = df['sentence_length'].std()

# 2. Category distribution
all_labels = [label for sublist in df['labels'] for label in sublist]
label_counts = Counter(all_labels)
label_df = pd.DataFrame(label_counts.items(), columns=['Label', 'Count']).sort_values(by='Count', ascending=False)

# 3. Heatmap for co-occurrence of logical fallacies
# Create a co-occurrence matrix
unique_labels = list(set(all_labels))
cooccurrence_matrix = pd.DataFrame(0, index=unique_labels, columns=unique_labels)

for labels in df['labels']:
    for label1, label2 in combinations(labels, 2):
        cooccurrence_matrix.loc[label1, label2] += 1
        cooccurrence_matrix.loc[label2, label1] += 1

# Generate and display results
# import ace_tools as tools

# Display average length and standard deviation
summary_stats = pd.DataFrame({'Metric': ['Average Length', 'Standard Deviation'], 'Value': [avg_length, std_length]})
# tools.display_dataframe_to_user(name="Sentence Length Statistics", dataframe=summary_stats)
print(summary_stats)
print(label_df)

# # Display category distribution
# tools.display_dataframe_to_user(name="Logical Fallacy Category Distribution", dataframe=label_df)

# Plot heatmap for co-occurrence
plt.figure(figsize=(12, 8))
# Create a mask for the upper triangle to display only the lower triangle
mask = np.triu(np.ones_like(cooccurrence_matrix, dtype=bool))
sns.heatmap(cooccurrence_matrix, cmap="Blues", mask=mask, annot=False, linewidths=0.5, square=True)
plt.title("Co-occurrence Heatmap of Logical Fallacies")
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.show()
