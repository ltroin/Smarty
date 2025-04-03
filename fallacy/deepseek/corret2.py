import asyncio
import json
from openai import OpenAI

# API
API_KEY = ""
BASE_URL = ""
deepseek_API_KEY = ""
deepseek_BASE_URL = ""
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
deepseek = OpenAI(api_key=deepseek_API_KEY, base_url=deepseek_BASE_URL)


def extract_json(raw_text: str) -> dict:
    try:
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

    max_retries = 5  # 增加重试次数
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                deepseek.chat.completions.create,
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content":
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
                    },
                    {"role": "user", "content": prompt},
                ]
            )
            result_text = response.choices[0].message.content.strip()

            # JSON
            if result_text:
                result_json = extract_json(result_text) or json.loads(result_text)
            else:
                raise ValueError("Empty API response")

            required_fields = ["logic_error", "logic_fallacies", "details"]
            if not all(field in result_json for field in required_fields):
                raise KeyError("Missing required fields")

            return {
                **result_json,
                "sentence": sentence
            }
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            await asyncio.sleep(2 ** attempt)

    # Flase return
    return {
        "logic_error": "error",
        "logic_fallacies": [],
        "details": "Maximum retries exceeded"
    }


async def repair_errors():
    json_file = 'deepseek_v3.json'

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    repair_targets = [
        idx for idx, entry in enumerate(data)
        if entry.get("logic_error") == "error"
           or "error" in entry.values()
    ]

    print(f"Found {len(repair_targets)} error entries to reprocess")

    batch_size = 300
    for i in range(0, len(repair_targets), batch_size):
        batch = repair_targets[i:i + batch_size]
        tasks = []

        for idx in batch:
            original_entry = data[idx]
            tasks.append(
                process_line(original_entry["sentence"])
            )

        new_results = await asyncio.gather(*tasks)

        for idx, result in zip(batch, new_results):
            data[idx].update({
                "logic_error": result["logic_error"],
                "logic_fallacies": result["logic_fallacies"],
                "details": result["details"]
            })

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {min(i + batch_size, len(repair_targets))}/{len(repair_targets)} entries")


if __name__ == '__main__':
    asyncio.run(repair_errors())