import asyncio
import csv
from openai import OpenAI
import json
from collections import OrderedDict

API_KEY = ""
BASE_URL = "https://api.deepbricks.ai/v1/"
deepseek_API_KEY = ""
deepseek_BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
deepseek = OpenAI(api_key=deepseek_API_KEY, base_url=deepseek_BASE_URL)

def extract_json(raw_text: str) -> dict:
    try:
        #Markdown  problem
        if raw_text.startswith("```json"):
            raw_text = raw_text[len("```json"):].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-len("```")].strip()
        return json.loads(raw_text)
    except Exception:
        return None

async def process_line(sentence: str) -> dict:
    prompt = f"""Judging this element:

{sentence}

Please return the result in JSON format as follows:
{{
  "sentence": "Sentence given",
  "logic_error": "Findings of the judgement, only lowercase yes or no",
  "logic_fallacies": "Select all the closest categorisations and rank them in order of closeness.",
  "details": "explicit explanation"
}}."""
    max_retries = 30
    attempt = 0
    result_text = ""
    while attempt < max_retries:
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": (
                        "You're an expert in logic."
                        "Here's a categorisation of the 14 logic errors."
                        "Determine whether the given sentence has logical errors and deal with them as required. "
                        "False dilemma: The presentation of an issue as having only two possible outcomes, either right or wrong, without recognising that additional alternatives may exist."
                        "Equivocation: The misleading use of a word or phrase that has multiple meanings, creating ambiguity and leading to confusion in interpretation or reasoning."
                        "False Premise: The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions. "
                        "False Analogy: The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference."
                        "Wrong Direction: The incorrect attribution of causality by reversing the cause-and-effect relationship, assuming the effect is the cause and the cause is the effect."
                        "Fallacy of composition: The mistaken assumption that what is true for a part of something must also be true for the whole, disregarding the possible differences between individual components and the entire entity."
                        "Begging the question: The use of a statement as both the premise and the conclusion, assuming the truth of what is to be proven instead of providing independent support. "
                        "False Cause: The incorrect assumption that a causal relationship exists between two events solely because one follows the other, failing to account for coincidence or other influencing factors."
                        "Inverse Error: The mistaken reasoning that if A implies B, then not A must imply not B, overlooking the possibility that B may still occur due to other factors."
                        "Improper transposition: The incorrect inference that if A implies B, then B must also imply A, failing to recognise that implication is not necessarily reversible."
                        "Improper Distribution or Addition: The erroneous reasoning that individual effects can be directly summed or distributed across a group without considering their actual impact or interaction."
                        "Contextomy: The act of selectively quoting or altering a statement, advertisement, or published material in a way that distorts its original meaning, often misrepresenting the intent of the original source. "
                        "Nominal Fallacy: The mistaken interpretation of a metaphorical or figurative expression as a literal statement, leading to a misunderstanding of its intended meaning. "
                        "Accident fallacy: The misapplication of a general rule to a specific case where exceptions should be considered, treating the rule as absolute without regard for context or relevant circumstances."

                    )},
                    {"role": "user", "content": prompt}
                ]
            )
            result_text = response.choices[0].message.content.strip()
            result_json = json.loads(result_text)
            return result_json
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} for sentence failed with error: {e}")
            if result_text:
                extracted = extract_json(result_text)
                if extracted is not None:
                    return extracted
            await asyncio.sleep(1)
    return {
        "error": "error: Failed after multiple retries",
        "original_sentence": sentence,
        "raw_response": result_text
    }

async def main():
    input_file = '../ruozhiba_high.csv'
    output_file = 'gpt_4o_ruozhiba_since.json'
    tasks = []
    sentences = []

    # CSV first row is sentence
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].strip():
                sentences.append(row[0].strip())

    for sentence in sentences:
        tasks.append(process_line(sentence))

    results = await asyncio.gather(*tasks)

    new_results = []
    idstart = 0
    for idx, result in enumerate(results):
        new_dict = OrderedDict()
        new_dict["id"] = idx + idstart + 1
        new_dict["sentence"] = sentences[idx]
        for key, value in result.items():
            if key != "sentence":
                new_dict[key] = value
        new_results.append(new_dict)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    asyncio.run(main())
