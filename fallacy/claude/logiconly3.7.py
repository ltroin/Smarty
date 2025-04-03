import anthropic
import asyncio
import csv
import json
from collections import OrderedDict

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


async def process_line(sentence: str) -> dict:
    prompt = f"""Judging this element:

{sentence}

Please return the result in JSON format as follows:
{{
  "sentence": "Sentence given",
  "logic_error": "Findings of the judgement, only lowercase yes or no",
  "details": "explicit explanation"
}}."""
    max_retries = 3
    attempt = 0
    result_text = ""
    while attempt < max_retries:
        try:
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-7-sonnet-20250219",  # Using proper model ID
                system="You're an expert in logic.Sentences will be given below, judge whether they are logical or not and output according to the specific requirement.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=9000
            )
            # The correct way to access Claude's response content
            result_text = response.content[0].text

            # Try to parse JSON directly
            result_json = extract_json(result_text)
            if result_json:
                return result_json
            else:
                attempt += 1
                print(f"Invalid JSON format in attempt {attempt}. Retrying...")
                await asyncio.sleep(1)

        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} for sentence failed with error: {e}")
            await asyncio.sleep(1)

    return {
        "error": "error: Failed after multiple retries",
        "original_sentence": sentence,
        "raw_response": result_text
    }


async def main():
    input_file = '../ruozhiba.csv'
    output_file = 'claude_3_7_sonnet_yes_or_no.json'
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
        for key, value in result.items():
            new_dict[key] = value
        new_results.append(new_dict)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    asyncio.run(main())