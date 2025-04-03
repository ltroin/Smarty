import asyncio
import csv
import json
from collections import OrderedDict
from openai import AsyncOpenAI, APIError
from tqdm.asyncio import tqdm_asyncio

# Configuration for DeepSeek API
DEEPSEEK_API_KEY = ""
DEEPSEEK_BASE_URL = ""

# Initialize async client
client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def extract_json(raw_text: str) -> dict:
    """Extract JSON from text, handling Markdown code blocks."""
    try:
        if raw_text.startswith("```json"):
            raw_text = raw_text[len("```json"):].lstrip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3].rstrip()
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return None


async def process_line(sentence: str, pbar: tqdm_asyncio, max_retries: int = 3) -> dict:
    """
    Process a sentence with DeepSeek API using async requests.

    Args:
        sentence: Input text to analyze
        pbar: Progress bar instance for updating
        max_retries: Maximum number of retry attempts
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


    system_prompt = """You're an expert in logic.
Here's a categorisation of the 14 logic errors.
Determine whether the given sentence has logical errors and deal with them as required. 
False dilemma: The presentation of an issue as having only two possible outcomes, either right or wrong, without recognising that additional alternatives may exist.
Equivocation: The misleading use of a word or phrase that has multiple meanings, creating ambiguity and leading to confusion in interpretation or reasoning.
False Premise: The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions. 
False Analogy: The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference.
Wrong Direction: The incorrect attribution of causality by reversing the cause-and-effect relationship, assuming the effect is the cause and the cause is the effect.
Fallacy of composition: The mistaken assumption that what is true for a part of something must also be true for the whole, disregarding the possible differences between individual components and the entire entity.
Begging the question: The use of a statement as both the premise and the conclusion, assuming the truth of what is to be proven instead of providing independent support. 
False Cause: The incorrect assumption that a causal relationship exists between two events solely because one follows the other, failing to account for coincidence or other influencing factors.
Inverse Error: The mistaken reasoning that if A implies B, then not A must imply not B, overlooking the possibility that B may still occur due to other factors.
Improper transposition: The incorrect inference that if A implies B, then B must also imply A, failing to recognise that implication is not necessarily reversible.
Improper Distribution or Addition: The erroneous reasoning that individual effects can be directly summed or distributed across a group without considering their actual impact or interaction.
Contextomy: The act of selectively quoting or altering a statement, advertisement, or published material in a way that distorts its original meaning, often misrepresenting the intent of the original source. 
Nominal Fallacy: The mistaken interpretation of a metaphorical or figurative expression as a literal statement, leading to a misunderstanding of its intended meaning. 
Accident fallacy: The misapplication of a general rule to a specific case where exceptions should be considered, treating the rule as absolute without regard for context or relevant circumstances."""

    result = {"sentence": sentence, "error": None}
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                # timeout=10
            )

            if json_data := extract_json(response.choices[0].message.content):
                result.update(json_data)
                break
            raise ValueError("Invalid JSON format")

        except (APIError, TimeoutError, ValueError) as e:
            if attempt >= max_retries - 1:
                result.update({
                    "error": f"Max retries exceeded: {str(e)}",
                    "logic_error": "no",
                    "logic_fallacies": [],
                    "details": ""
                })
            await asyncio.sleep(0.5 * (attempt + 1))
        finally:
            pbar.update(1)

    return result


async def main():
    """Main processing pipeline with progress tracking"""
    input_csv = '../ruozhiba_high.csv'
    output_json = 'deepseek_results.json'

    # Read sentences from CSV
    with open(input_csv, 'r', encoding='utf-8') as f:
        sentences = [row[0].strip() for row in csv.reader(f) if row and row[0].strip()]

    # Create progress bar
    max_retries = 50
    with tqdm_asyncio(
            total=len(sentences) * max_retries,
            desc="rocessing Sentences",
            unit="attempt",
            colour="green",
            ncols=100
    ) as pbar:
        tasks = [process_line(sentence, pbar) for sentence in sentences]
        results = await asyncio.gather(*tasks)

    # Format and save results
    ordered_results = [
        OrderedDict([("id", idx + 1)] + list(item.items()))
        for idx, item in enumerate(results)
    ]

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(ordered_results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    asyncio.run(main())