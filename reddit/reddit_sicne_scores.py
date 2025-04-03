import pandas as pd
import json
import asyncio
import time
from openai import AsyncOpenAI

# ========== Configuration ==========

MAX_RETRIES = 40
RETRY_DELAY = 0.5  # seconds between retries

# ========== Load CSV ==========
# actually reddit data
df = pd.read_csv("ruozhiba_label.csv")

# ========== Label Ordering for Sorting ==========
definitions_order = [
    "False dilemma", "Equivocation", "False Premise", "False Analogy", "Wrong Direction",
    "Fallacy of composition", "Begging the question", "False Cause", "Inverse Error",
    "Improper transposition", "Improper Distribution or Addition", "Contextomy",
    "Nominal Fallacy", "Accident fallacy"
]

def get_sort_index(label):
    primary = label.split(',')[0].strip()
    return definitions_order.index(primary) if primary in definitions_order else float('inf')

# ========== System Prompt ==========
system_prompt = {
    "role": "system",
    "content":
        "You are a professional logical fallacy evaluator. Your task is to review a file containing sentences that illustrate specific logical fallacies and assign each a score based on how well the sentence demonstrates the intended fallacy (as indicated by its type field). "
        "Evaluate them holistically based on your understanding of how these fallacies manifest in real-world human communication and reasoning. Do not use code-based methods. Use critical judgment.\n\n"
        "Scoring Guide:\n"
        "- Score 0: The sentence makes no sense or does not exhibit the intended logical error.\n"
        "- Score 1: The sentence shows only minor applicability of the fallacy in its type field.\n"
        "- Score 2: The sentence largely demonstrates the fallacy.\n"
        "- Score 3: The sentence is a perfect example of the logical fallacy as described in its type.\n\n"
        "Definitions:\n" + "\n".join([
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
        ])
}

# ========== Evaluate One Sentence with Retry ==========
async def evaluate_with_retries(client, sentence, label, csv_id):
    user_prompt = {
        "role": "user",
        "content": f'Sentence: "{sentence}"\nLabel: "{label}"\n'
                   'Return the result in this JSON format: '
                   '{"sentence":"...", "label":"...", "Score":..., "Explanation":"..."}'
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[system_prompt, user_prompt]
            )
            reply = response.choices[0].message.content.strip()
            parsed = json.loads(reply)
            parsed["id"] = csv_id  # 使用CSV中的ID
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

    tasks = [
        evaluate_with_retries(client, row["Sentence"], row["Label"], row["ID"])
        for _, row in df.iterrows()
    ]

    results = await asyncio.gather(*tasks)

    sorted_results = sorted(results, key=lambda x: get_sort_index(x["label"]))

    with open("evaluation_results_reliable.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=2)

    print("All sentences scored and saved to evaluation_results_reliable.json")

# ========== Execute ==========
if __name__ == "__main__":
    asyncio.run(main())
