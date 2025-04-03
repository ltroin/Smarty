import json

LENGTH = 0
def count_logic_errors(filename):
    """Count the number of times logic_error is 'yes' in a JSON file."""
    global LENGTH
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    LENGTH = 220
    # take the first 502 entries
    data = data[:220]
    print(f"Length of {filename}: {len(data)}")
    return sum(1 for entry in data if entry.get('logic_error', '').lower() == 'yes')

def calculate_f1(fp, fn, tp):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

files  =["claude_3_7_sonnet.json","claude_3_7_sonnet_thinking.json", "claude_3_5.json" , "gpt_4o.json" ,"llama_3_1_405b.json" ,"o3_mini.json","deepseek_v3.json","deepseek_r1.json","grok_2.json"]
# files = ["claude_3_5.json", "gpt_4o.json", "llama_3_1_405b.json", "o3_mini.json"]

results = {}

for filename in files:
    filename_yes = filename.replace(".json", "_2_2.json")
    logic_yes = count_logic_errors(filename_yes)
    # good_file = filename.replace(".json", "_good.json")
    # print(good_file)
    logic_yes_good = count_logic_errors(filename.replace(".json", "_good.json"))
    
    logic_no = LENGTH - logic_yes
    logic_no_good = LENGTH - logic_yes_good

    # in yes file,  no prediction is false negative / by all no
    # in good file, yes prediction is false positive / by all yes

    FN = logic_no/(logic_no_good+logic_no)
    FP = logic_yes_good/(logic_yes+logic_yes_good)
    TP = logic_yes/(logic_yes+logic_yes_good)

    f1 = round(calculate_f1(FP, FN, TP), 3)
    
    results[filename_yes] = {"fp": FP, "fn": FN, "f1": f1}

# Output results
for file, result in results.items():
    print(f"{file}: {result}")
