import csv
import re
import json  # Import json module to write JSON output

def clean_value(value):
    """Remove surrounding double quotes if present and strip whitespace."""
    if value.startswith("\"\"") and value.endswith("\"\""):
        value = value[1:-1].strip()
    value = value.replace("’", "'").replace("`", "'")
    return value

def convert_inner_quotes(text):
    """Convert inner double quotes to single quotes, keeping outer quotes unchanged."""
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", text)

temp = []

csv_fallacy_map = {}
fallacy_totals = {}
with open("generated_ruozhiba.csv", 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:                
        # sentence = clean_value(row[3].strip())
        # sentence = convert_inner_quotes(sentence)  # Apply the transformation
        # fallacy_type = row[2].strip().strip('"')
        sentence = clean_value(row[0].strip())
        sentence = convert_inner_quotes(sentence)
        fallacy_type = row[1].strip().strip('"')

        fallacy_list = [f.strip().lower() for f in fallacy_type.split(',') if f.strip()]
        
        csv_fallacy_map[sentence] = fallacy_type
        
        temp.append(sentence)
        # Tally total counts for each fallacy type from the CSV
        for fallacy in fallacy_list:
            fallacy_totals[fallacy] = fallacy_totals.get(fallacy, 0) + 1

# Save temp list as a JSON file
with open("list.json", "w", encoding="utf-8") as f:
    json.dump(temp, f, ensure_ascii=False, indent=4)
print(len(csv_fallacy_map))

def format_sentence(sentence):

    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")

    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)





def process_json_file(data, csv_fallacy_map):

    fallacy_correct = {fallacy: 0 for fallacy in fallacy_totals.keys()}

    for entry in data:
        logic_error = entry.get('logic_error', '').lower()
        fallacies = entry.get('logic_fallacies', [])
        
        # Convert string fallacies to list
        if isinstance(fallacies, str):
            fallacies = [f.strip().lower() for f in fallacies.split(',')]
        else:
            fallacies = [f.lower() for f in fallacies]
        
        sentence = format_sentence(entry['sentence'])
        if sentence in diff_list:
                diff_list.remove(sentence)
        else:
            print(sentence)
        if logic_error == 'yes':
            # Get correct fallacy from CSV mapping
            correct_fallacy = csv_fallacy_map.get(sentence, '').lower()
            
            if not correct_fallacy:
                print(sentence)
                # pass
            # print(corre)
            # print(correct_fallacy)
            # print(fallacies)
            for fallacy in correct_fallacy.split(','):
                if fallacy in fallacies:
                    fallacy_correct[fallacy] += 1
                # else:
                #     print(f"Fallacy {fallacy} not found in {fallacies}")
            
            
    return fallacy_correct

results = {}
# Process JSON data
# diff_list = list(csv_fallacy_map.keys())

files  =["claude_3_7_sonnet.json","claude_3_7_sonnet_thinking.json", "claude_3_5.json" , "gpt_4o.json" ,"llama_3_1_405b.json" ,"o3_mini.json","deepseek_v3.json","deepseek_r1.json","grok_2.json"]

for filename in files:
    filename = filename.replace(".json", "_2_2.json")
    with open(filename, 'r', encoding='utf-8')  as f:
        data = json.load(f)
    diff_list = list(csv_fallacy_map.keys())
    print(len(diff_list))

    ratios = process_json_file(data, csv_fallacy_map)
    results[filename] = ratios


with open("generated_results.txt", "w") as f:
    for filename, ratios in results.items():
        print(f"Results for {filename}:", file=f)
        for fallacy, ratio in ratios.items():
            print(f"  {fallacy}: {ratio:.3f}", file=f)
        print(file=f)

    # list total fallacies numbers
    print(fallacy_totals, file=f)


print(diff_list)




