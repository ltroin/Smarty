import csv
import re
import json
import os  # For directory access

DATA_FILE = "SmartyPat_augmented" # Just modify the folder name

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
# Step 1: Load CSV mapping (augmented sentences → fallacy types)
# -------------------------------------------------
csv_fallacy_map = {}
fallacy_totals = {}
temp = []

with open("SmartyPat_augmented_label.csv", 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        sentence = clean_value(row[0].strip())
        sentence = convert_inner_quotes(sentence)
        fallacy_type = row[1].strip().strip('"')

        fallacy_list = [f.strip().lower() for f in fallacy_type.split(',') if f.strip()]
        csv_fallacy_map[sentence] = fallacy_type
        temp.append(sentence)

        # Count total per fallacy type
        for fallacy in fallacy_list:
            fallacy_totals[fallacy] = fallacy_totals.get(fallacy, 0) + 1

# Save all sentence strings for inspection
with open("list.json", "w", encoding="utf-8") as f:
    json.dump(temp, f, ensure_ascii=False, indent=4)

print("Loaded sentence count from CSV:", len(csv_fallacy_map))

# -------------------------------------------------
# Utility: Normalize sentence for consistent matching
# -------------------------------------------------
def format_sentence(sentence):
    """Normalize sentence formatting to match CSV structure."""
    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)

# -------------------------------------------------
# Scoring: Match predicted fallacies against CSV
# -------------------------------------------------
def process_json_file(data, csv_fallacy_map, diff_list):
    """Evaluate how many times each fallacy is correctly predicted."""
    fallacy_correct = {fallacy: 0 for fallacy in fallacy_totals.keys()}

    for entry in data:
        logic_error = entry.get('logic_error', '').lower()
        fallacies = entry.get('logic_fallacies', [])

        if isinstance(fallacies, str):
            fallacies = [f.strip().lower() for f in fallacies.split(',')]
        else:
            fallacies = [f.lower() for f in fallacies]

        sentence = format_sentence(entry['sentence'])

        if sentence in diff_list:
            diff_list.remove(sentence)
        else:
            print("Unexpected sentence not in CSV:", sentence)

        if logic_error == 'yes':
            correct_fallacy = csv_fallacy_map.get(sentence, '').lower()
            if not correct_fallacy:
                print("Missing in CSV:", sentence)
                continue
            for fallacy in correct_fallacy.split(','):
                if fallacy in fallacies:
                    fallacy_correct[fallacy] += 1

    return fallacy_correct

# -------------------------------------------------
# Step 2: Evaluate JSON files in specified folder
# -------------------------------------------------
results = {}
data_dir = DATA_FILE
json_files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

for filename in json_files:
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    diff_list = list(csv_fallacy_map.keys())  # Reset unmatched list
    print(f"\n🔍 Processing {filename}, total sentences to match: {len(diff_list)}")

    ratios = process_json_file(data, csv_fallacy_map, diff_list)
    results[filename] = ratios

# -------------------------------------------------
# Step 3: Output Results to Text File
# -------------------------------------------------
with open("augmented_results.txt", "w") as f:
    for filename, ratios in results.items():
        print(f"Results for {filename}:", file=f)
        for fallacy, count in ratios.items():
            print(f"  {fallacy}: {count}", file=f)
        print(file=f)

    print("✅ Total ground truth fallacy counts:", file=f)
    print(fallacy_totals, file=f)

# -------------------------------------------------
# Step 4: Display unmatched sentences (optional)
# -------------------------------------------------
print("\n🧩 Sentences from CSV not found in any JSON file:")
print(diff_list)
