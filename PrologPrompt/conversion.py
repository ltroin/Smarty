import os
import random
import pandas as pd
import openai

# ——— CONFIGURATION ——————————————————————————————————————————————————————
API_KEY = "YOUR_API_KEY"    # leave empty as requested
CSV_PATH = "SmartyPat_label.csv"
EXAMPLES_DIR = "."          # where your *_examples.txt live
OUTPUT_DIR = "outputs"
MAX_SENTENCES = 25

# Initialize OpenAI client
client = openai.OpenAI(api_key=API_KEY)

# Fallacy definitions
definitions = {
    "False Premise": "The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions.",
    "False Analogy": "The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference.",
    "Wrong Direction": "The incorrect attribution of causality by reversing the cause-and-effect relationship, assuming the effect is the cause and the cause is the effect.",
    "Fallacy of composition": "The mistaken assumption that what is true for a part of something must also be true for the whole, disregarding the possible differences between individual components and the entire entity.",
    "Begging the question": "The use of a statement as both the premise and the conclusion, assuming the truth of what is to be proven instead of providing independent support.",
    "False Cause": "The incorrect assumption that a causal relationship exists between two events solely because one follows the other, failing to account for coincidence or other influencing factors.",
    "Inverse Error": "The mistaken reasoning that if A implies B, then not A must imply not B, overlooking the possibility that B may still occur due to other factors.",
    "Improper transposition": "The incorrect inference that if A implies B, then B must also imply A, failing to recognise that implication is not necessarily reversible.",
    "Improper Distribution or Addition": "The erroneous reasoning that individual effects can be directly summed or distributed across a group without considering their actual impact or interaction.",
    "Contextomy": "The act of selectively quoting or altering a statement, advertisement, or published material in a way that distorts its original meaning, often misrepresenting the intent of the original source.",
    "Accident fallacy": "The misapplication of a general rule to a specific case where exceptions should be considered, treating the rule as absolute without regard for context or relevant circumstances."
}

# ——— UTILITY FUNCTIONS ——————————————————————————————————————————————————

def load_sentences(csv_path, label):
    """
    Load all sentences from CSV where 3rd column == label.
    Sample up to MAX_SENTENCES if there are more.
    """
    df = pd.read_csv(csv_path, header=None, encoding='utf-8')
    # assuming: idx 2 = fallacy label, idx 3 = sentence
    matches = df[df[2] == label][3].dropna().astype(str).tolist()
    if len(matches) > MAX_SENTENCES:
        return random.sample(matches, MAX_SENTENCES)
    return matches

def load_facts(fallacy_type, examples_dir):
    """
    Read Prolog facts from .txt file named like:
      false_premise_examples.txt
    """
    fname = fallacy_type.lower().replace(" ", "_") + "_examples.txt"
    path = os.path.join(examples_dir, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No examples file for {fallacy_type}: {path}")
    with open(path, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def generate_fallacy_sentences(fallacy_type, definition, sentences, facts):
    """
    Call OpenAI to generate 5 new sentences for this fallacy.
    """
    prompt = f"""
    Instruction: Generate 20 new {fallacy_type} Prolog knowledge combinations. Study the style of the sentences in the provided list and transform the given Prolog facts into natural language sentences that follow a similar style and structure.

    Query:
    List: {sentences}
    PrologFacts: {facts}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4000
    )
    return response.choices[0].message.content

# ——— MAIN WORKFLOW —————————————————————————————————————————————————————

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for fallacy_type, definition in definitions.items():
        print(f"→ Processing: {fallacy_type}")

        # 1. load up to 25 style sentences
        sentences = load_sentences(CSV_PATH, fallacy_type)
        if not sentences:
            print(f"  • Warning: no sentences found for '{fallacy_type}', skipping.")
            continue

        # 2. load all Prolog facts from the corresponding .txt
        try:
            facts = load_facts(fallacy_type, EXAMPLES_DIR)
        except FileNotFoundError as e:
            print(f"  • {e}")
            continue

        # 3. call the API
        generated = generate_fallacy_sentences(fallacy_type, definition, sentences, facts)

        # 4. save to file
        out_path = os.path.join(OUTPUT_DIR, f"{fallacy_type.replace(' ', '_')}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(generated + "\n")

        print(f"  • Saved output to {out_path}")

if __name__ == "__main__":
    main()
