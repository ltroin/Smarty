import csv
import re
import json
import os  # Required for directory listing

DATA_FILE = "SmartyPat" # Just modify the folder name


# -------------------------------------------------
# Utility: Clean value from CSV
# -------------------------------------------------
def clean_value(value):
    """Remove surrounding double quotes if present and strip whitespace."""
    if value.startswith("\"\"") and value.endswith("\"\""):
        value = value[1:-1].strip()
    value = value.replace("’", "'").replace("`", "'")
    return value


# -------------------------------------------------
# Utility: Convert inner double quotes to single quotes
# -------------------------------------------------
def convert_inner_quotes(text):
    """Convert inner double quotes to single quotes, keeping outer quotes unchanged."""
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", text)


# -------------------------------------------------
# Step 1: Load CSV into a mapping {sentence: fallacy_type}
# -------------------------------------------------
temp = []
csv_fallacy_map = {}

with open("SmartyPat_label.csv", 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        sentence = clean_value(row[3].strip())
        sentence = convert_inner_quotes(sentence)
        fallacy_type = row[2].strip().strip('"')

        fallacy_list = [f.strip() for f in fallacy_type.split(',') if f.strip()]
        csv_fallacy_map[sentence] = fallacy_type
        temp.append(sentence)

# Save list of sentences to JSON for reference
with open("list_SmartyPat.json", "w", encoding="utf-8") as f:
    json.dump(temp, f, ensure_ascii=False, indent=4)

print("Number of unique sentences in CSV:", len(csv_fallacy_map))


# -------------------------------------------------
# Utility: Normalize sentence format from JSON
# -------------------------------------------------
def format_sentence(sentence):
    """Normalize sentence by stripping quotes and standardizing punctuation."""
    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)


# Initialize sentence difference tracking and fallacy count stats
diff_list = list(csv_fallacy_map.keys())
num_count = {}


# -------------------------------------------------
# Scoring Function: Calculate model performance per sentence
# -------------------------------------------------
def calculate_score(entry, csv_fallacy_map, filename):
    """Calculate a score for each sentence prediction."""
    score = 0.0
    logic_error = entry.get('logic_error', '').lower()
    fallacies = entry.get('logic_fallacies', [])

    # Ensure fallacies is a lowercase list
    if isinstance(fallacies, str):
        fallacies = [f.strip().lower() for f in fallacies.split(',')]
    else:
        fallacies = [f.lower() for f in fallacies]

    sentence = format_sentence(entry['sentence'])
    if sentence in diff_list:
        diff_list.remove(sentence)

    if logic_error == 'yes':
        correct_fallacy = csv_fallacy_map.get(sentence, '').lower()
        if not correct_fallacy:
            print("Missing in CSV:", sentence)

        num_count[filename] = num_count.get(filename, 0) + len(fallacies)

        for i, fallacy in enumerate(fallacies):
            weight = 1 / (i + 1)
            if fallacy in correct_fallacy:
                score += weight
            else:
                score -= weight
    elif logic_error == 'no':
        for i in range(13):
            score -= 1 / (i + 1)

    return round(score, 3)


# -------------------------------------------------
# Step 2: Process all JSON files in the directory
# -------------------------------------------------
results = {}

data_dir = DATA_FILE
json_files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

for filename in json_files:
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    final_score = 0
    for entry in data:
        score = calculate_score(entry, csv_fallacy_map, filename)
        final_score += score

    results[filename] = round(final_score, 3)

# -------------------------------------------------
# Step 3: Print final results
# -------------------------------------------------
print("\nFinal Scores Per File:\n")
print(results)

print("\nSentences in CSV but not found in any JSON file:\n")
print(diff_list)

print("\nFallacy Count Statistics (per file):\n")
print(num_count)
