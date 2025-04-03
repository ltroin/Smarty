import anthropic
import asyncio
import json
from typing import Dict, Any, Optional


API_KEY = ""
client = anthropic.Anthropic(api_key=API_KEY)


def extract_json(raw_text: str) -> dict:
    try:
        # Markdown problem
        if raw_text.startswith("```json"):
            raw_text = raw_text[len("```json"):].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-len("```")].strip()
        return json.loads(raw_text)
    except Exception:
        return None


def extract_text_response(content_list):
    for item in content_list:
        if item.type == "text":
            return item.text
    raise ValueError("No 'text' type content found in response.")



# Example usage:
# result_text = extract_text_response(response)


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
                client.messages.create,
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 8000
                },
                system=(
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
                ),
                messages=[
                    {"role": "user", "content": prompt}
                ],

            )
            # The correct way to access Claude's response content


            result_text = extract_text_response(response.content)
            print(result_text)
            # Try to parse JSON directly

            extracted_json = extract_json(result_text)

            if extracted_json:
                return extracted_json
            else:
                print(f"Failed to parse JSON from response: {result_text[:100]}...")
                attempt += 1

        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} for sentence failed with error: {e}")
            await asyncio.sleep(2)  # Increased backoff

    return {
        "error": "error: Failed after multiple retries",
        "original_sentence": sentence,
        "raw_response": result_text[:500]  # Truncate long responses
    }


async def fix_json():
    json_file = 'claude_3_7_sonnet_good_V2_thinking.json'

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return

    error_indices = []
    tasks = []

    for idx, entry in enumerate(data):
        if entry.get("error") == "error: Failed after multiple retries":
            sentence = entry.get("original_sentence") or entry.get("sentence")
            if sentence:
                tasks.append(process_line(sentence))
                error_indices.append(idx)
            else:
                print(f"Warning: No sentence found for entry at index {idx}")

    if tasks:
        print(f"{len(tasks)} errors found, processing...")
        new_results = await asyncio.gather(*tasks)

        for index, new_res in zip(error_indices, new_results):
            data[index].update(new_res)

        # Clean up entries
        for entry in data:
            entry.pop("error", None)
            entry.pop("original_sentence", None)
            entry.pop("raw_response", None)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("JSON has been updated successfully.")
    else:
        print("No errors found to fix.")


if __name__ == '__main__':
    asyncio.run(fix_json())