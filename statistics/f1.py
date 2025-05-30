import os
import json

# Number of entries to evaluate per file
LENGTH = 220


def count_logic_errors(filepath):
    """Count entries where logic_error == 'yes' in the first LENGTH items."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)[:LENGTH]
    print(f"Loaded {len(data)} entries from {filepath}")
    return sum(1 for e in data if e.get('logic_error', '').lower() == 'yes')


def calculate_f1(fp, fn, tp):
    """Compute F1 score from false-positive (FP), false-negative (FN), and true-positive (TP) rates."""
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    return (2 * precision * recall / (precision + recall)) if (precision + recall) else 0


# Base paths for each variant folder
BASE_DIR = os.getcwd()
BASE_DIRS = {
    "Smartypat": os.path.join(BASE_DIR, "Smartypat"),
    "Smartypat_augmented": os.path.join(BASE_DIR, "Smartypat_augmented"),
}
HIGHQ_DIR = os.path.join(BASE_DIR, "Smartypat_logic_sound")  # gold-standard data

# Discover all model names (strip ".json") from the base folder
models = [f[:-5] for f in os.listdir(BASE_DIRS["Smartypat"]) if f.endswith(".json")]

# Prepare a results dict: results[model][variant] = metrics
results = {model: {} for model in models}

# Loop over each variant folder first (to sort by variant)
for variant in sorted(BASE_DIRS):
    folder = BASE_DIRS[variant]
    for model in models:
        # Build file paths: same filename in each variant folder
        pred_path = os.path.join(folder, f"{model}.json")
        gold_path = os.path.join(HIGHQ_DIR, f"{model}.json")

        # Count predicted yes's and gold yes's
        yes_pred = count_logic_errors(pred_path)
        yes_gold = count_logic_errors(gold_path)

        # Compute predicted no's and gold no's
        no_pred = LENGTH - yes_pred
        no_gold = LENGTH - yes_gold

        # Compute error rates:
        FN = no_pred / (no_gold + no_pred) if (no_gold + no_pred) else 0
        FP = yes_gold / (yes_pred + yes_gold) if (yes_pred + yes_gold) else 0
        TP = yes_pred / (yes_pred + yes_gold) if (yes_pred + yes_gold) else 0

        # Compute F1
        f1 = round(calculate_f1(FP, FN, TP), 3)

        # Store metrics
        results[model][variant] = {
            "fp": round(FP, 3),
            "fn": round(FN, 3),
            "tp": round(TP, 3),
            "f1": f1
        }

# Print summary grouped by variant
print(f"{'Variant':20} {'Model':40} {'FP':6} {'FN':6} {'TP':6} {'F1':6}")
print("-" * 90)  # adjust width as needed
for variant in sorted(BASE_DIRS):
    for model in sorted(models):
        m = results[model][variant]
        print(f"{variant:20} {model:40} "
              f"{m['fp']:<6.3f} {m['fn']:<6.3f} "
              f"{m['tp']:<6.3f} {m['f1']:<6.3f}")
