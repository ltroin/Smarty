import csv
import re
import json

def clean_value(value):
    """Remove surrounding double quotes if present and strip whitespace."""
    if value.startswith("\"\"") and value.endswith("\"\""):
        value = value[1:-1].strip()
    value = value.replace("’", "'").replace("`", "'")
    return value

def convert_inner_quotes(text):
    """Convert inner double quotes to single quotes, keeping outer quotes unchanged."""
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", text)

def format_sentence(sentence):
    """Similar logic as before, to strip single quotes, etc."""
    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)

def calculate_score(entry, csv_fallacy_map):
    """Same logic as before to compute a numeric score per sentence+model."""
    score = 0.0
    logic_error = entry.get('logic_error', '').lower()
    fallacies = entry.get('logic_fallacies', [])

    # Convert string fallacies to list
    if isinstance(fallacies, str):
        fallacies = [f.strip().lower() for f in fallacies.split(',')]
    else:
        fallacies = [f.lower() for f in fallacies]

    sentence = format_sentence(entry['sentence'])

    if logic_error == 'yes':
        # Get correct fallacy from CSV mapping
        correct_fallacy = csv_fallacy_map.get(sentence, '').lower()
        # If there's no correct fallacy, or not found, your code might skip or handle differently
        for i, fallacy in enumerate(fallacies):
            weight = 1 / (i + 1)
            if fallacy in correct_fallacy:
                score += weight
            else:
                score -= weight
    elif logic_error == 'no':
        # Apply descending penalty series
        for i in range(13):
            score -= 1 / (i + 1)

    return round(score, 3)

# -------------------------------------------------
# 1. Load your CSV fallacy map as before.
# -------------------------------------------------
csv_fallacy_map = {}
with open("ruozhiba_label.csv", 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        sentence = clean_value(row[0].strip())
        sentence = convert_inner_quotes(sentence)
        fallacy_type = row[11].strip().strip('"')
        csv_fallacy_map[sentence] = fallacy_type

print("Total sentences in CSV:", len(csv_fallacy_map))

# -------------------------------------------------
# 2. Go through each of your JSON files, compute scores,
#    and store them by (sentence, model).
# -------------------------------------------------
files = [
    "claude_3_7_sonnet.json",
    "claude_3_5.json",
    "gpt_4o.json",
    "llama_3_1_405b.json",
    "o3_mini.json",
    "deepseek_v3.json",
    "deepseek_r1.json",
    "grok_2.json"
]

# model_scores[sentence][filename] = numeric_score
model_scores = {}

for filename in files:
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        if entry['logic_error'].lower() != 'yes':
            continue
        sentence = format_sentence(entry['sentence'])
        score = calculate_score(entry, csv_fallacy_map)
        
        # Ensure there's a sub-dict for each sentence
        if sentence not in model_scores:
            model_scores[sentence] = {}
        # Store the score for this model/file
        model_scores[sentence][filename] = score

# -------------------------------------------------
# 3. For each sentence, check if it appears in *all* models.
#    Then sum up the scores (or compute average).
# -------------------------------------------------
scores_list = []
for sentence, per_model_dict in model_scores.items():
    # Only consider sentences that show up in *all* files
    if len(per_model_dict) == len(files):
        total_score = sum(per_model_dict[model_file] for model_file in files)
        # If you want the average:
        # avg_score = total_score / len(files)
        scores_list.append((sentence, total_score))

# -------------------------------------------------
# 4. Sort by ascending total score and pick the first 10
# -------------------------------------------------
scores_list.sort(key=lambda x: x[1])  # Sort by total_score ascending
lowest_10 = scores_list[:10]

print("\nTop 10 sentences with the lowest total score across all models:\n")
for idx, (s, sc) in enumerate(lowest_10, start=1):
    print(f"{idx}. Score={sc:.3f} | Sentence: {s}")
