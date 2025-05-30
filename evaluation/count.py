import pandas as pd
import json
import asyncio
from openai import AsyncOpenAI
from collections import defaultdict

# ========== Configuration ==========
API_KEY = ""
BASE_URL = ""
MAX_RETRIES = 50
RETRY_DELAY = 0.5  # seconds between retries

# ========== Definitions ==========
DEFINITIONS = {
    "false dilemma": "The presentation of an issue as having only two possible outcomes, either right or wrong, without recognising that additional alternatives may exist.",
    "equivocation": "The misleading use of a word or phrase that has multiple meanings, creating ambiguity and leading to confusion in interpretation or reasoning.",
    "false premise": "The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions.",
    "false analogy": "The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference.",
    "wrong direction": "The incorrect attribution of causality by reversing the cause-and-effect relationship, assuming the effect is the cause and the cause is the effect.",
    "fallacy of composition": "The mistaken assumption that what is true for a part of something must also be true for the whole, disregarding the possible differences between individual components and the entire entity.",
    "begging the question": "The use of a statement as both the premise and the conclusion, assuming the truth of what is to be proven instead of providing independent support.",
    "false cause": "The incorrect assumption that a causal relationship exists between two events solely because one follows the other, failing to account for coincidence or other influencing factors.",
    "inverse error": "The mistaken reasoning that if A implies B, then not A must imply not B, overlooking the possibility that B may still occur due to other factors.",
    "improper transposition": "The incorrect inference that if A implies B, then B must also imply A, failing to recognise that implication is not necessarily reversible.",
    "improper distribution or addition": "The erroneous reasoning that individual effects can be directly summed or distributed across a group without considering their actual impact or interaction.",
    "contextomy": "The act of selectively quoting or altering a statement, advertisement, or published material in a way that distorts its original meaning, often misrepresenting the intent of the original source.",
    "nominal fallacy": "The mistaken interpretation of a metaphorical or figurative expression as a literal statement, leading to a misunderstanding of its intended meaning.",
    "accident fallacy": "The misapplication of a general rule to a specific case where exceptions should be considered, treating the rule as absolute without regard for context or relevant circumstances."
}

# ========== Label Ordering for Sorting ==========
DEFINITIONS_ORDER = [
    "False dilemma", "Equivocation", "False Premise", "False Analogy", "Wrong Direction",
    "Fallacy of composition", "Begging the question", "False Cause", "Inverse Error",
    "Improper transposition", "Improper Distribution or Addition", "Contextomy",
    "Nominal Fallacy", "Accident fallacy"
]


def get_sort_index(label: str) -> int:
    primary = label.split(',')[0].strip()
    try:
        return DEFINITIONS_ORDER.index(primary)
    except ValueError:
        return float('inf')


def get_definitions(label: str) -> str:
    """
    Return the definition(s) for the given label(s), case-insensitive.
    """
    names = [l.strip().lower() for l in label.split(',')]
    lines = []
    for name in names:
        definition = DEFINITIONS.get(name)
        if definition:
            lines.append(f"{name.title()}: {definition}")
    return "\n".join(lines)

# ========== System Prompt ==========
SCORING_GUIDE = ("""
You are a professional logical fallacy evaluator.
Your task is to review a file containing sentences that illustrate specific logical fallacies and assign each a score based on how well the sentence demonstrates the intended fallacy (as indicated by its type field).
Evaluate them more holistically based on your understanding of how these fallacies manifest in real-world human communication and reasoning.
Do not use code-based method.

Scoring Guide:
- Score 0: The sentence makes no sense or does not exhibit the intended logical error.
- Score 1: The sentence shows only minor applicability of the fallacy in its type field.
- Score 2: The sentence largely demonstrates the fallacy.
- Score 3: The sentence is a perfect example of the logical fallacy as described in its type.
"""

)

SYSTEM_PROMPT = {
    "role": "system",
    "content": SCORING_GUIDE
}

# ========== Evaluate One Sentence with Retry ==========
async def evaluate_with_retries(client, sentence: str, label: str, csv_id: int) -> dict:
    definition_text = get_definitions(label)
    user_content = (
        f'Sentence: "{sentence}"\n'
        f'Label: "{label}"\n'
        f'Definition:\n{definition_text}\n'
        'Return the result in this JSON format: '
        '{"sentence": "...", "label": "...", "score": ..., "explanation": "..."}'
    )
    user_prompt = {"role": "user", "content": user_content}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[SYSTEM_PROMPT, user_prompt]
            )
            reply = response.choices[0].message.content.strip()
            parsed = json.loads(reply)
            parsed["id"] = csv_id
            return parsed
        except Exception as e:
            print(f"[Retry {attempt}/{MAX_RETRIES}] ID {csv_id} failed: {e}")
            await asyncio.sleep(RETRY_DELAY)

    return {
        "sentence": sentence,
        "label": label,
        "Score": -1,
        "Explanation": f"Failed after {MAX_RETRIES} retries.",
        "id": csv_id
    }

# ========== Main Async Processing Function ==========
async def main():
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    df = pd.read_csv("SmartyPat_augmented_label.csv", header=None, names=["sentence", "label"])

    tasks = []
    # df.values is an ndarray of shape (n_rows, 2)
    for idx, (sentence, label) in enumerate(df.values, start=1):
        tasks.append(
            evaluate_with_retries(client, sentence, label, idx)
        )

    results = await asyncio.gather(*tasks)
    sorted_results = sorted(results, key=lambda x: get_sort_index(x["label"]))
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=2)

    # Read back the results just written
    with open("evaluation_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Initialise the statistical structure
    stats = defaultdict(lambda: {"counts": {0: 0, 1: 0, 2: 0, 3: 0}, "sum": 0, "total": 0})

    # Iterate through all the entries and accumulate the number of individual scores and the total score
    for entry in data:
        label = entry["label"]
        score = entry.get("score", entry.get("Score"))
        if isinstance(score, (int, float)):
            stats[label]["counts"][score] += 1
            stats[label]["sum"] += score
            stats[label]["total"] += 1

    # Print the distribution of scores and mean scores for each label
    print("\n=== Score Statistics by Label ===")
    for label, info in stats.items():
        avg = info["sum"] / info["total"] if info["total"] else 0
        counts = info["counts"]
        print(f'{label}: counts → 0:{counts[0]} 1:{counts[1]} 2:{counts[2]} 3:{counts[3]}, average → {avg:.2f}')

    print("All sentences scored and saved to evaluation_results.json")


if __name__ == "__main__":
    asyncio.run(main())
