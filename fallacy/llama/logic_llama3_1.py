import asyncio
import csv
import json
from collections import OrderedDict
from openai import OpenAI
from evaluation.reddit_sicne_scores import MAX_RETRIES

# Configuration
API_KEY = ""  # Fill in your API key
BASE_URL = ""  # Optional: Fill in your custom base URL if needed
MODEL = "llama_3_1_405b"
INPUT_FILE = '../SmartyPat.csv'
OUTPUT_FILE = f'{MODEL}_logic.json'
MAX_RETRIES = MAX_RETRIES
CONCURRENCY_LIMIT = 5  # Limit number of concurrent requests

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

def extract_json(raw_text: str) -> dict:
    """
    Extract JSON from response, handling potential Markdown formatting issues.
    """
    try:
        if raw_text.startswith("```json"):
            raw_text = raw_text[len("```json"):].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-len("```")].strip()
        return json.loads(raw_text)
    except Exception:
        return None

async def process_line(sentence: str) -> dict:
    """
    Process a single sentence by querying the language model.
    Includes retry with exponential backoff and JSON extraction fallback.
    """
    prompt = f"""Judging this element:

{sentence}

Please return the result in JSON format as follows:
{{
  "sentence": "Sentence given",
  "logic_error": "Findings of the judgement, only lowercase yes or no",
  "details": "explicit explanation"
}}."""

    attempt = 0
    result_text = ""

    async with semaphore:  # Concurrency control
        while attempt < MAX_RETRIES:
            try:
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=MODEL,
                    temperature=0,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You're an expert in logic. Sentences will be given below. "
                                "Judge whether they are logical or not and output according to the specific requirement."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                result_text = response.choices[0].message.content.strip()
                return json.loads(result_text)
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed for sentence: {sentence[:30]}... Error: {e}")
                # Try to extract JSON from malformed response
                if result_text:
                    extracted = extract_json(result_text)
                    if extracted is not None:
                        return extracted
                await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff (1s, 2s, 4s...)

    return {
        "error": "Failed after multiple retries",
        "original_sentence": sentence,
        "raw_response": result_text
    }

async def main():
    """
    Main routine: loads CSV, runs sentence evaluation, and writes results to output JSON.
    """
    tasks = []
    sentences = []

    # Load sentences from CSV file (assumes one sentence per row, first column)
    with open(INPUT_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].strip():
                sentences.append(row[0].strip())

    # Create processing tasks
    for sentence in sentences:
        tasks.append(process_line(sentence))

    # Execute all tasks asynchronously with concurrency control
    results = await asyncio.gather(*tasks)

    # Format results with consistent ID indexing
    new_results = []
    for idx, result in enumerate(results):
        new_dict = OrderedDict()
        new_dict["id"] = idx + 1
        for key, value in result.items():
            new_dict[key] = value
        new_results.append(new_dict)

    # Write output to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    asyncio.run(main())
