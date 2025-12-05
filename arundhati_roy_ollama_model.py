#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import pandas as pd
from tqdm import tqdm
from llama_cpp import Llama
import re

model_path = "/Users/anantupadhiyay/models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf"

print("Loading Qwen model...")
llm = Llama(
    model_path=model_path,
    n_ctx=2048,   
    n_threads=8   
)

csv_path = "youtube_comments_arundhati_mothermary.csv"  # ensure file is in the same directory
df = pd.read_csv(csv_path)

if "text" not in df.columns:
    raise ValueError("CSV must contain a 'text' column for sentiment analysis.")

print(f"Loaded {len(df)} comments from CSV\n")

def analyze_sentiment(comment):
    """Use Qwen model to classify sentiment."""
    prompt = f"Classify the sentiment of this YouTube comment as Positive, Negative, or Neutral:\n\"{comment}\""
    try:
        output = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        raw_result = output["choices"][0]["message"]["content"].strip()

        # Extract sentiment word
        match = re.search(r'(Positive|Negative|Neutral)', raw_result, re.IGNORECASE)
        if match:
            return match.group(1).capitalize()
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {e}"

tqdm.pandas()

# Test on first 1000 comments — change to df.copy() for full dataset
df_subset = df.head(1000).copy()

print("⚙️ Starting sentiment analysis...\n")
df_subset['sentiment'] = df_subset['text'].progress_apply(analyze_sentiment)


output_csv = "arundhati_roy_youtube_comments_.csv"
df_subset.to_csv(output_csv, index=False)

print(f"\nSentiment analysis complete!")
print(f"Results saved to: {output_csv}\n")
print("Example output:")
print(df_subset.head(10))
