#-------------------------------------------------------------------------------
# Copyright (c) 2026 Rahil Piyush Mehta, Manish Motwani, Pushpak Katkhede, Kausar Y. Moshood, and Huwaida Rahman Yafie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------

import os
import csv
import sys
import re
import json
import numpy as np
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from sentence_transformers import SentenceTransformer
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
import nltk

# Prevent parallel tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Download stopwords
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Input arguments
preprocessed_dir_path = sys.argv[1]
manually_curated_defects_path = sys.argv[2]

# Read valid issue URLs
valid_issue_urls = set()
with open(manually_curated_defects_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        issue_url = row.get('issue_url', '').strip()
        if issue_url:
            valid_issue_urls.add(issue_url)

# Preprocessing helper
def simple_tokenize(text):
    text = re.sub(r"http\S+|www\S+", "", text.lower())
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    return [t for t in text.split() if t not in stop_words]

# Load documents
docs, issue_urls, patched_file_types_list, tokenized_docs = [], [], [], []
for filename in os.listdir(preprocessed_dir_path):
    if "rest_api_issue" in filename and filename.endswith(".csv"):
        with open(os.path.join(preprocessed_dir_path, filename), 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                issue_url = row.get('issue_url', '').strip()
                if issue_url not in valid_issue_urls:
                    continue
                text = row.get('text_for_topic_modeling', '').strip()
                if text:
                    docs.append(text)
                    issue_urls.append(issue_url)
                    ft = row.get('patched_file_types', '').strip()
                    patched_file_types_list.append(",".join(set(ft.split("|"))))
                    tokenized_docs.append(simple_tokenize(text))

print(f"Loaded {len(docs)} valid documents.")

# Topic modeling function
def run_topic_modeling(index, docs, issue_urls, patched_file_types_list,
                       embedding_model_name="all-MiniLM-L6-v2",
                       min_cluster_size=10, min_samples=None,
                       eps=0.3, metric="cosine",
                       min_df=2, max_df=200,
                       representation_model=None):

    embedding_model = SentenceTransformer(embedding_model_name)
    embeddings = embedding_model.encode(docs, show_progress_bar=True)

    # DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
    labels = dbscan.fit_predict(embeddings)

    # Filter valid clusters
    label_counts = Counter(labels)
    valid_labels = {l for l, c in label_counts.items() if l != -1 and c >= min_cluster_size}

    filtered = [(d, e, u, p) for d, e, u, p, l in zip(docs, embeddings, issue_urls, patched_file_types_list, labels) if l in valid_labels]
    if not filtered:
        raise ValueError("No valid clusters formed.")

    fdocs, fembs, furls, fpfts = zip(*filtered)
    fembs = np.array(fembs)

    # Save filtered data
    json.dump(fdocs, open(f"filtered_docs_{index}.json", "w"), indent=2)
    np.save(f"filtered_embeddings_{index}.npy", fembs)
    np.save(f"dbscan_labels_{index}.npy", labels)

    # Vectorizer
    vectorizer = CountVectorizer(min_df=min_df, max_df=max_df, ngram_range=(1, 2), stop_words="english")

    # BERTopic
    topic_model = BERTopic(
        vectorizer_model=vectorizer,
        representation_model=representation_model,
        calculate_probabilities=True,
        verbose=True
    )
    topics, probs = topic_model.fit_transform(fdocs, embeddings=fembs)

    results_df = pd.DataFrame({
        "issue_url": furls,
        "patched_file_types": fpfts,
        "text_for_topic_modeling": fdocs,
        "topic": topics
    })

    topic_model.get_topic_info().to_csv(f"topic_summary_{index}.csv", index=False)
    topic_model.get_document_info(fdocs).to_csv(f"document_topic_assignments_{index}.csv", index=False)

    # Silhouette
    mask = np.array(topics) != -1
    sil_score = silhouette_score(fembs[mask], np.array(topics)[mask]) if np.sum(mask) > 1 else None

    return topic_model, results_df, sil_score

# Grid search
representation_model = KeyBERTInspired()
results = []
config = 1
results_file = "hyperparameter_tuning_dbscan_607.csv"

top_configs = [
    {"config_id": 344, "min_size": 30, "min_samples": 10, "eps": 0.5, "min_df": 2, "max_df": 300},
   
]
for params in top_configs:
    print(f"\nRunning model for original config {params['config_id']} ...")
    model, result_df, sil_score = run_topic_modeling(
        index=params["config_id"],  # <-- use the original config number
        docs=docs,
        issue_urls=issue_urls,
        patched_file_types_list=patched_file_types_list,
        min_cluster_size=params["min_size"],
        min_samples=params["min_samples"],
        eps=params["eps"],
        metric="cosine",
        min_df=params["min_df"],
        max_df=params["max_df"],
        representation_model=representation_model
    )
    print(f"Starting model {config}...")


    # Save model and results
    model.save(f"bertopic_model_{params['config_id']}")
    result_df.to_csv(f"topic_modeling_results_{params['config_id']}.csv", index=False)
