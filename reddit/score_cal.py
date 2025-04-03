import json
import os
import time
import pandas as pd

# 1. Read the evaluation_results_reliable.json data
with open('evaluation_results_reliable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count the occurrences of each score (0, 1, 2, 3)
score_counts = {score: 0 for score in [0, 1, 2, 3]}
for record in data:
    score = record.get("Score")
    if score in score_counts:
        score_counts[score] += 1

print("Count of records for each score:")
for score in sorted(score_counts):
    print(f"Score {score}: {score_counts[score]}")

# 2. Filter low scores (0, 1, 2) and high scores (3) and extract required fields.
# Note: Replace 'row' with 'id' since the JSON now contains an 'id' field.
low_scores = [
    {
        "sentence": record.get("sentence"),
        "score": record.get("Score"),
        "label": record.get("label"),
        "id": record.get("id")
    }
    for record in data if record.get("Score") in [0, 1]
]

high_scores_new = [
    {
        "sentence": record.get("sentence"),
        "score": record.get("Score"),
        "label": record.get("label"),
        "explanation": record.get("Explanation"),
        "id": record.get("id")
    }
    for record in data if record.get("Score") in [2, 3]
]

# 3. Sort both low_scores and high_scores_new in ascending order based on 'id'
low_scores.sort(key=lambda x: x.get("id"))
high_scores_new.sort(key=lambda x: x.get("id"))

# 4. Write low_scores to low_scores.json (overwrite) and sleep for 5 seconds after writing
with open('low_scores.json', 'w', encoding='utf-8') as f:
    json.dump(low_scores, f, ensure_ascii=False, indent=4)
print("Low score records have been written to low_scores.json")
time.sleep(5)

# 5. Append high_scores_new to high_scores.json
#    Read existing data if available, append new records, sort, and remove duplicates based on 'id'
high_file = 'high_scores.json'
if os.path.exists(high_file):
    with open(high_file, 'r', encoding='utf-8') as f:
        try:
            existing_high = json.load(f)
        except json.JSONDecodeError:
            existing_high = []
else:
    existing_high = []

combined_high = existing_high + high_scores_new
combined_high.sort(key=lambda x: x.get("id"))

# Remove duplicates: keep only the last record for each unique 'id'
unique_high = {rec['id']: rec for rec in combined_high}.values()
combined_high = sorted(unique_high, key=lambda x: x.get("id"))

with open(high_file, 'w', encoding='utf-8') as f:
    json.dump(combined_high, f, ensure_ascii=False, indent=4)
print("High score records have been appended to high_scores.json")
time.sleep(5)

# 6. Remove rows from ruozhiba_label.csv that have ids matching those in combined_high.
#    Note: The first column in the CSV is 'id' which contains the related id data.
csv_file = 'ruozhiba_label.csv'
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    # Extract all id values from combined_high
    ids_to_remove = {record.get("id") for record in combined_high}
    # Filter the DataFrame to remove rows where the 'id' is in ids_to_remove
    df_filtered = df[~df['ID'].isin(ids_to_remove)]
    df_filtered.to_csv(csv_file, index=False)
    print(f"Rows with matching high score ids have been removed from {csv_file}")
else:
    print(f"CSV file {csv_file} does not exist. Please check the file name or path.")
