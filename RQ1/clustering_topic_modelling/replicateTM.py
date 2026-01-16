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
import ast
import re
import nltk
from collections import Counter
from bertopic import BERTopic
from hdbscan import HDBSCAN
from scipy.cluster import hierarchy as sch
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
from bertopic.representation import KeyBERTInspired
import json
import numpy as np
from nltk.corpus import stopwords

os.environ["TOKENIZERS_PARALLELISM"] = "false"


#min_samples = 3
#min_cluster_size = 3
#clusterer = HDBSCAN(min_samples=min_samples, min_cluster_size=min_cluster_size)


# Path to preprocessed CSV files
preprocessed_dir_path = sys.argv[1]
manually_curated_defects_path = sys.argv[2]
valid_issue_urls = set()

# Single-configuration output directory
OUTPUT_DIR = "/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/single_configuration"
os.makedirs(OUTPUT_DIR, exist_ok=True)

icount=0
with open(manually_curated_defects_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')  # Assuming tab-separated values
    for row in reader:
        issue_url = str(row.get('issue_url', '')).strip()
        if issue_url:
            icount = icount + 1
            valid_issue_urls.add(issue_url)

# Initialize list to hold all documents
docs = []
issue_urls = []
patched_file_types_list = []
tokenized_docs = []


nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
def simple_tokenize(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)         # remove URLs
    text = re.sub(r"[^\w\s]", "", text)                # remove punctuation
    text = re.sub(r"\d+", "", text)                    # remove numbers
    tokens = text.split()
    return [t for t in tokens if t not in stop_words]


# Iterate over all CSV files in the folder
for filename in os.listdir(preprocessed_dir_path):
    print(f"Processing: {filename}")
    if "rest_api_issue" in filename and filename.endswith(".csv"):
        csv_file_path = os.path.join(preprocessed_dir_path, filename)
        print(f"Processing: {csv_file_path}")
        # Open and read the CSV file
        issue_count = 0
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                issue_url = str(row.get('issue_url', '')).strip()
                if issue_url not in valid_issue_urls:
                    continue
                text_for_topic_modeling = str(row.get('text_for_topic_modeling', '')).strip()
                patched_file_types = str(row.get('patched_file_types', '')).strip()
                if text_for_topic_modeling:  # Only process non-empty text
                    issue_count += 1
                    docs.append(text_for_topic_modeling)
                    issue_urls.append(issue_url)
                    patched_file_types_list.append(",".join(set(patched_file_types.split("|"))))

                    tokenized = simple_tokenize(text_for_topic_modeling)
                    tokenized_docs.append(tokenized)
        print(f"Found {issue_count} rest api defects.")
print(f"Loaded {len(docs)} documents.")

# Fine-tune your topic representations
representation_model = KeyBERTInspired()

def run_topic_modeling(
    index, 
    docs,
    issue_urls,
    patched_file_types_list,
    embedding_model_name="all-MiniLM-L6-v2",
    hdbscan_min_cluster_size=10,
    hdbscan_min_samples=None,
    dbscan_metric='cosine',
    dbscan_eps=0.3,
    vectortizer_min_df=2,
    vectortizer_max_df=200,
    representation_model=representation_model

):

  # Load embedding model
    embedding_model = SentenceTransformer(embedding_model_name)
    dbscan_model = DBSCAN(
        eps=dbscan_eps,         # Distance threshold (tune this!)
        min_samples=hdbscan_min_samples,   # Minimum docs per cluster
        metric=dbscan_metric  # Try also "cosine"
    )
    embeddings = embedding_model.encode(docs, show_progress_bar=True)
    labels = dbscan_model.fit_predict(embeddings)
    
     #  Filter out noise and small clusters
    cluster_counts = Counter(labels)
    valid_labels = {
        label for label, count in cluster_counts.items()
        if label != -1 and count >= hdbscan_min_cluster_size
    }

    filtered_docs = [doc for doc, label in zip(docs, labels) if label in valid_labels]
    filtered_embeddings = [emb for emb, label in zip(embeddings, labels) if label in valid_labels]
    filtered_embeddings = np.array(filtered_embeddings)
    filtered_issue_urls = [url for url, label in zip(issue_urls, labels) if label in valid_labels]
    filtered_patched_file_types = [ft for ft, label in zip(patched_file_types_list, labels) if label in valid_labels]

    with open(os.path.join(OUTPUT_DIR, f"filtered_docs_{index}.json"), "w", encoding="utf-8") as f:
        json.dump(filtered_docs, f, ensure_ascii=False, indent=2)

    # Save filtered_embeddings as .npy
    np.save(
        os.path.join(OUTPUT_DIR, f"filtered_embeddings_{index}.npy"),
        filtered_embeddings
    )

    # Save all labels for future filtering (optional but useful)
    np.save(
        os.path.join(OUTPUT_DIR, f"dbscan_labels_{index}.npy"),
        labels
    )

    print(f"Remaining docs after DBSCAN: {len(filtered_docs)}")
    print(f"Embeddings length after DBSCAN: {len(filtered_embeddings)}")

    if len(filtered_docs) == 0:
        raise ValueError("No valid clusters formed.")



    vectorizer_model = CountVectorizer(
        min_df=vectortizer_min_df,
        max_df=vectortizer_max_df,
        ngram_range=(1, 2),
        stop_words="english"
    )

    vectorizer_model.fit(filtered_docs)
    print(f"# terms: {len(vectorizer_model.vocabulary_)}")


    # Initialize BERTopic
    topic_model = BERTopic(
        embedding_model=None,
        umap_model=None,
        hdbscan_model=None,
        vectorizer_model=vectorizer_model,
        verbose=True,
        representation_model=None,
        calculate_probabilities=False
    )
    
    print(f"Length docs: {len(filtered_docs)}")
    print(f"Length embeddings: {len(filtered_embeddings)}")
    print(f"Shape embeddings: {filtered_embeddings.shape if hasattr(filtered_embeddings, 'shape') else 'no shape'}")

    # Fit and transform
    topics, probs = topic_model.fit_transform(filtered_docs, embeddings=filtered_embeddings)
    
    # Prepare results dataframe
    results_df = pd.DataFrame({
        "issue_url": filtered_issue_urls,
        "patched_file_types": filtered_patched_file_types,
        "text_for_topic_modeling": filtered_docs,
        "topic": topics
    })

    # Save summaries
    topic_info_df = topic_model.get_topic_info()
    doc_info_df = topic_model.get_document_info(filtered_docs)

    topic_info_df.to_csv("topic_summary_" + str(index) + ".csv", index=False)
    doc_info_df.to_csv("document_topic_assignments_" + str(index) + ".csv", index=False)

    print("Topic Info:")
    print(topic_info_df)
    print("\nDocument Info:")
    print(doc_info_df)

    # Compute silhouette score (excluding outliers)
    mask = np.array(topics) != -1
    if np.sum(mask) > 1:
        sil_score = silhouette_score(filtered_embeddings[mask], np.array(topics)[mask])
        print(f"\nSilhouette Score (excluding outliers): {sil_score:.3f}")
    else:
        sil_score = None
        print("\nSilhouette Score not computed: insufficient clustered docs.")

    return topic_model, results_df, sil_score, filtered_embeddings, labels, doc_info_df, topic_info_df




# tokenized_docs is your list of token lists


from configs import CONFIGS, CONFIG_ID

if CONFIG_ID not in CONFIGS:
    raise ValueError(f"Configuration {CONFIG_ID} not defined.")

cfg = CONFIGS[CONFIG_ID]

print(f"\nRunning SINGLE configuration #{CONFIG_ID}")
print(cfg)



# Run single configuration
topic_model, results_df, sil_score, filtered_embeddings, labels, doc_info_df, topic_info_df = run_topic_modeling(
    index=CONFIG_ID,
    docs=docs,
    issue_urls=issue_urls,
    patched_file_types_list=patched_file_types_list,
    hdbscan_min_cluster_size=cfg["min_cluster_size"],
    hdbscan_min_samples=cfg["min_samples"],
    dbscan_metric=cfg["metric"],
    dbscan_eps=cfg["eps"],
    vectortizer_min_df=cfg["min_df"],
    vectortizer_max_df=cfg["max_df"],
    representation_model=representation_model
)

# Step 2: Save model, embeddings, and labels
topic_model.save(os.path.join(OUTPUT_DIR, f"bertopic_model_{CONFIG_ID}"))
np.save(os.path.join(OUTPUT_DIR, f"filtered_embeddings_{CONFIG_ID}.npy"), filtered_embeddings)
np.save(os.path.join(OUTPUT_DIR, f"dbscan_labels_{CONFIG_ID}.npy"), labels)


# Step 3: Save CSV summaries
doc_info_df.to_csv(os.path.join(OUTPUT_DIR, f"document_topic_assignments_{CONFIG_ID}.csv"), index=False)
topic_info_df.to_csv(os.path.join(OUTPUT_DIR, f"topic_summary_{CONFIG_ID}.csv"), index=False)
results_df.to_csv(os.path.join(OUTPUT_DIR, f"topic_modeling_results_{CONFIG_ID}.csv"), index=False)


# Step 4: Generate HTML visualizations
topic_model.visualize_topics().write_html(os.path.join(OUTPUT_DIR, f"topic_overview_{CONFIG_ID}.html"))
topic_model.visualize_barchart().write_html(os.path.join(OUTPUT_DIR, f"topic_sizes_{CONFIG_ID}.html"))
topic_model.visualize_hierarchy().write_html(os.path.join(OUTPUT_DIR, f"topic_hierarchy_{CONFIG_ID}.html"))
topic_model.visualize_term_rank().write_html(os.path.join(OUTPUT_DIR, f"term_ranks_{CONFIG_ID}.html"))


# Step 5: Save topic URLs CSV and TXT
topic_urls_df = results_df[["topic", "issue_url"]].dropna().sort_values("topic")
topic_urls_df.to_csv(os.path.join(OUTPUT_DIR, f"topic_urls_{CONFIG_ID}.csv"), index=False)

with open(os.path.join(OUTPUT_DIR, f"topic_urls_{CONFIG_ID}.txt"), "w") as f:
    for topic, group in topic_urls_df.groupby("topic"):
        f.write(f"Topic {topic}\n")
        for url in group["issue_url"]:
            f.write(f"{url}\n")
        f.write("\n")

print(f"All files for configuration {CONFIG_ID} saved in {OUTPUT_DIR}")
