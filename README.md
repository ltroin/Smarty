# 🧠 SmartyPat-Bench & Augmented: Codebase for Logical Fallacy Evaluation

This repository supports the paper:

**Socrates or Smartypants: Testing Logic Reasoning Capabilities of Large Language Models (LLMs) with Logic Programming-based Test Oracles**

📄 **Website:** Coming soon!

**Table of Contents:**

- [🚀 Summary](#-summary)
- [📁 Repository Structure](#-repository-structure)
- [📊 Dataset Descriptions](#-dataset-descriptions)
- [🛠️ Key Components](#-key-components)
- [✅ Reproduction Guide](#-reproduction-guide)

## 🚀 Summary

This repo contains the full implementation of **SmartyPat-Bench**, a benchmark designed to evaluate logical reasoning in LLMs, and **SmartyPat**, a logic programming-powered system that automatically generates logically fallacious sentences via Prolog and LLMs.

We offer two key datasets:

- **SmartyPat-Bench**: 502 real-world fallacious Reddit posts, manually labeled with logical fallacy types.
- **SmartyPat-Bench-Augmented**: Thousands of synthetic sentences automatically generated with fine-grained Prolog logic and transformed to natural language via LLMs.

---

## 📁 Repository Structure

```
📁 Project Root
├── 📁 csv/                  # All labeled evaluation datasets in CSV format
├── 📁 evaluation/           # Storing scoring functions already scored
│   └── 📄 count             # Functions for scoring the SPBA
├── 📁 fallacy/              # Main evaluation scripts; organized by model subfolders
│   ├── 📁 <MODEL>/  
│   │   └── 📄 fallacy_*.py  # Fallacy type classification scripts (per model)
│   ├── 📁 <RES>/            # Storage of generated data
│   └──📄 main.py            # Utility to batch run all fallacy evaluation scripts
├── 📁 fig/                  # Scripts to generate figures (e.g., F1 score plots, label distribution)
├── 📁 PrologPrompt/         # Prolog generation and conversion tools
│   ├── 📄 prompt.py         # Claude-based Prolog prompt constructor
│   ├── 📄 conversion.py     # Natural language to Prolog converter
│   └── 📄 fallacies.pl      # Prolog rules and fallacy definitions
├── 📁 res/                  # Stores all model outputs for post-analysis and review
├── 📁 statistics/           # Scripts for computing F1 scores and analyzing fallacy distributions
├── 📄 requirements.txt      # Dependency list for environment setup
└── 📄 README.md             # Project documentation
```

---

## 📊 Dataset Descriptions

### `csv/SmartyPat.csv` and `csv/SmartyPat_label.csv`

- Contains manually curated Reddit posts with logical fallacies.
- Labeled with 14 fallacy types (see Section 2.1 of the paper).
- Logical structures are normalized to `(p1 ∧ p2 ∧ ... ∧ pn) → q` form.
- See Section 3.2 of the paper for full construction process.

### `csv/SmartyPat_augmented.csv` and `csv/SmartyPat_augmented_label.csv`


This dataset is automatically generated using a structured 3-stage Prolog-based pipeline located in `PrologPrompt/`. Below is a step-by-step reproduction guide for how the **SmartyPat-Bench-Augmented (SPBA)** dataset was constructed:

#### Step-by-Step SPBA Generation Guide

##### Step 1: Define Fallacy Rules

* **File**: `PrologPrompt/fallacies.pl`
* This file contains a manually constructed Prolog rule base that encodes the logical structure of each fallacy type.
* Each rule expresses the inference patterns that constitute a fallacy.

>  You don’t need to modify this file unless you are introducing new fallacy types.

##### Step 2:  Generate Prolog Facts via LLM

* **File**: `PrologPrompt/prompt.py`
* Run this script to automatically prompt an LLM (e.g., Claude 3.7 Sonnet Extend Thinking) to generate fallacy-relevant Prolog facts.
* Output files are saved as `{fallacy_type}_examples.txt` in the working directory.

```bash
python PrologPrompt/prompt.py
```

> Ensure the API key and model configuration are correctly set inside the script.

##### Step 3:  Convert Facts to Natural Language


* **File**: `PrologPrompt/conversion.py`
* This script reads `<{fallacy_type}_examples.txt` files from Step 2 and transforms them into natural language sentences that preserve the original logical structure.
* Sentences are saved in the `outputs/` directory (automatically created), using the format `outputs/{fallacy_type}.txt`.

```bash
python PrologPrompt/conversion.py
```

##### Final CSV:

* `csv/SmartyPat_augmented.csv`: Unlabeled generated fallacious sentences.
* `csv/SmartyPat_augmented_label.csv`: The same sentences with assigned fallacy type labels.

These datasets form the **SmartyPat-Bench-Augmented (SPBA)** benchmark used throughout the paper.

### `csv/SmartyPat_logic_sound.csv`

- Control dataset of 502 logically sound sentences (for false positive testing).
- Collected from C4 and FineWeb; length-matched to Reddit data.

---

## 🛠️ Key Components

### `fallacy/`

- Contains main evaluation scripts for each model (e.g., `gpt_4o/fallacy_*.py`).
- Each script determines whether a sentence contains a fallacy and which type.
- Run all scripts using:

```bash
python fallacy/main.py
```

> 📌 Before running, configure the API key, base URL, and input file path in each fallacy_*.py.

### `evaluation/count.py`

Used to score the SmartyPat-Bench-Augmented (SPBA) sentences.

Produces the scores seen in Table 3 and Figure 5 of the paper.

Output: evaluation_results.json.

> ⚠️ Requires manual API key configuration and valid URL setup. To test, use: `csv/SmartyPat_augmented_label.csv`

### `fig/`

`F1_*.py` : Draws Figure 4 (F1 performance across models).

`fallacy_label_*.py` : Draws Figure 5 (fallacy type breakdown).

### `PrologPrompt/`

`fallacies.pl` : Contains all Prolog rules used by SmartyPat.

`prompt.py` : LLM prompt generator for Prolog-based generation.

`conversion.py` : Converts sentences into Prolog-compatible logical form.

### `statistics/`

`f1.py` : Computes F1 scores.

`fallacy_score.py` : Summarizes label distributions.

`fallacy_count.py` : Checks generation consistency.

`word_cloud.py` : Generates Figure 6

## ✅ Reproduction Guide

> 📌 Please carefully follow the steps below to reproduce the experimental results as presented in the paper. Each step explains the purpose of the script, configuration requirements, expected output, and where the output will be saved.

---

### 1. 📦 Environment Setup

Before running any experiments, install all required Python dependencies:

```bash
pip install -r requirements.txt
```

> This installs libraries for API calls, CSV/JSON processing, and visualization.

### 2. 🔍 Logical Fallacy Evaluation with LLMs

#### Script:

~~~
python fallacy/main.py
~~~

#### Purpose:

This script automatically traverses each model-named folder inside `fallacy/` (e.g., `gpt_4o/`, `claude_3_5/`) and runs all `fallacy_*.py` scripts inside them.

Each `fallacy_*.py` script:

* Loads a dataset (`SmartyPat.csv` or `SmartyPat_augmented.csv`).
* Sends each sentence to an LLM via API.
* Judges whether the sentence contains a fallacy and identifies its type.

#### Configuration:

In each `fallacy_*.py`:

* Set your **API key** and **Base URL**.
* Choose the input dataset:
  * `csv/SmartyPat.csv` for evaluating the original human-written benchmark.
  * `csv/SmartyPat_augmented.csv` for evaluating the auto-generated benchmark.

#### Output:

* A JSON file for each model, saved in a folder named after the input CSV (e.g., `SmartyPat_augmented/claude_3_5.json`).
* Each file contains the model’s predictions for every sentence (fallacy presence and type).

### 3. 🧾 Generating Figures

#### A. Figure 4 – F1 Score Performance

```bash
python fig/F1_<model>.py
```

* Reads the LLM prediction results from `fallacy/` subfolders.
* Computes F1 scores across all 14 fallacy types.
* Plots F1 score bar charts per model.

#### B. Figure 5 – Fallacy Type Distribution

```bash
python fig/fallacy_label_<model>.py
```

* Aggregates prediction outcomes by fallacy type.
* Visualizes how different models perform per fallacy.

#### Output:

* All generated figures are saved to the `fig/` folder.

---

### 4. 📈 Statistical Analysis

These scripts support metric computation and data integrity checks.

#### A. F1 Score Calculation (for Figure 4)

```bash
python statistics/f1.py
```

* Computes F1 scores from labeled vs. predicted fallacy types.
* Input: `*_label.csv` files and corresponding model outputs in `res/`.

#### B. Fallacy Label Statistics (for Figure 5 & Table 8)

```bash
python statistics/fallacy_score.py
```

* Tallies how many times each fallacy type appears in predictions.
* Used for label distribution plots and confusion matrix data.

#### C. Sentence Count Check

```bash
python statistics/fallacy_count.py
```

* Verifies the correct number of sentences were evaluated per model.

#### D. Word Cloud Generation (Figure 6)

```bash
python statistics/word_cloud.py
```

* Visualizes the most frequent words in the datasets using a word cloud

### 5. 📋 Evaluation (Figure 3 & Tabel 5)

Figure 3 visualizes the quality distribution of automatically generated fallacious sentences in **SmartyPat-Bench-Augmented (SPBA)**.

#### Script:

```bash
python evaluation/count.py
```

#### Purpose

This script automatically evaluates each sentence in `csv/SmartyPat_augmented_label.csv`, assigning a quality score from **0** to **3** according to how accurately it reflects its intended fallacy type. The generated scores are then used to produce:

- **Figure 5**: the distribution of quality scores across all fallacies
- **Table 3**: a detailed breakdown of score counts for each fallacy type and score level

#### Configuration:

Inside `count.py`:

* Set your OpenAI API key and URL.
* Set:

```
file = "csv/SmartyPat_augmented_label.csv"
```

#### Output:

* `evaluation_results.json`: Stores scoring results for each sentence, including:

  * Sentence ID
  * Fallacy type
  * Assigned score (0–3)
* Console output: A summary table showing, **for each fallacy type**:

  * Number of sentences scored as 0, 1, 2, and 3
  * Average score for the fallacy type

### Verification:

After automatic scoring via LLM (e.g., GPT-4o), results are **checked** to ensure scoring consistency and accuracy—especially for subtle or borderline examples.

#### Connection to Paper:

These results directly support **Figure 3** and **Table 5** of the paper. For complete logs and annotation protocols, please refer to the supplementary materials: 🔗 [Anonymous Supplementary Repo](https://anonymous.4open.science/r/supplementary_experiments-5CDB)
