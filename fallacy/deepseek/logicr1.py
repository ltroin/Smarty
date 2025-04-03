import asyncio
import csv
import json
from collections import OrderedDict
from openai import OpenAI  # DeepSeek is compatible with OpenAI SDK

# DeepSeek API configuration
deepseek_API_KEY = "s"  # Replace with your DeepSeek API Key
deepseek_BASE_URL = ""  # Base URL for DeepSeek API

# Initialize DeepSeek client
deepseek_client = OpenAI(api_key=deepseek_API_KEY, base_url=deepseek_BASE_URL)

def extract_json(raw_text: str) -> dict:
    """
    Extract JSON data from raw text.
    Supports Markdown-style JSON (```json```).
    """
    try:
        # Handle Markdown-formatted JSON
        if raw_text.startswith("```json"):
            raw_text = raw_text[len("```json"):].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-len("```")].strip()
        return json.loads(raw_text)
    except Exception:
        return None

async def process_line(sentence: str) -> dict:
    """
    Use DeepSeek API to process a single sentence, detect logic errors, and return the result.
    """
    prompt = f"""Judging this element:

{sentence}

Please return the result in JSON format as follows:
{{
  "sentence": "Sentence given",
  "logic_error": "Findings of the judgement, only lowercase yes or no",
  "logic_fallacies": "Select all the closest categorisations and rank them in order of closeness.",
  "details": "explicit explanation"
}}."""
    max_retries = 50  # Maximum retry attempts
    attempt = 0
    result_text = ""

    while attempt < max_retries:
        try:
            # Call DeepSeek API
            response = await asyncio.to_thread(
                deepseek_client.chat.completions.create,
                model="deepseek-reasoner",  # Use DeepSeek model
                messages=[
                    {
                        "role": "system",
                        "content": (
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
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            result_text = response.choices[0].message.content.strip()
            result_json = extract_json(result_text)  # Extract JSON data
            if result_json:
                return result_json
            else:
                raise ValueError("Failed to extract JSON from response.")
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} for sentence failed with error: {e}")
            await asyncio.sleep(1)  # Wait 1 second before retrying

    # If all retries fail, return error message
    return {
        "error": "Failed after multiple retries",
        "original_sentence": sentence,
        "raw_response": result_text,
    }

async def main():
    """
    Main function: read CSV file, process each sentence, and save results to a JSON file.
    """
    input_file = '../ruozhiba_high.csv'  # Input CSV file
    output_file = 'deepseek_r1_since.json'  # Output JSON file
    tasks = []
    sentences = []

    # Read CSV file
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].strip():
                sentences.append(row[0].strip())

    # Create a task for each sentence
    for sentence in sentences:
        tasks.append(process_line(sentence))

    # Concurrently execute all tasks
    results = await asyncio.gather(*tasks)

    # Format results and save to JSON file
    new_results = []
    for idx, result in enumerate(results):
        new_dict = OrderedDict()
        new_dict["id"] = idx + 1
        for key, value in result.items():
            new_dict[key] = value
        new_results.append(new_dict)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    asyncio.run(main())
