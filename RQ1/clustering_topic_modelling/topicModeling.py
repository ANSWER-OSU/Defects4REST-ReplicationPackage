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

    # Save filtered_docs as JSON
    with open("filtered_docs_" + str(index) +".json", "w", encoding="utf-8") as f:
        json.dump(filtered_docs, f, ensure_ascii=False, indent=2)

    # Save filtered_embeddings as .npy
    np.save("filtered_embeddings_" + str(index) + ".npy", filtered_embeddings)

    # Save all labels for future filtering (optional but useful)
    np.save("dbscan_labels_" + str(index) +".npy", labels)
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

    vectorizer_model.fit(docs)
    print(f"# terms: {len(vectorizer_model.vocabulary_)}")


    # Initialize BERTopic
    topic_model = BERTopic(
        embedding_model=None,
        umap_model=None,
        hdbscan_model=None,
        vectorizer_model=vectorizer_model,
        verbose=True,
        representation_model=None,
        calculate_probabilities=True
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

    return topic_model, results_df, sil_score


# tokenized_docs is your list of token lists
results = []
counter = 1

results_file = "hyperparameter_tuning_dbscan_607_replicateICSE26.csv"

for min_size in [10, 20, 30, 40, 50]:
    for min_samples in [10, 20, 30]:
        for metric in ["cosine"]:
            for eps in [0.5, 0.6, 0.7]:
                for min_df in [2, 3, 4, 5]:
                    for max_df in [300, 400, 500, 600, 700]:
                        try:
                            print(f"Counter={counter}\nTrying min_cluster_size={min_size}, min_samples={min_samples}, metric={metric}, eps={eps}, min_df={min_df}, max_df={max_df}")
                            topic_model, results_df, sil_score = run_topic_modeling(
                                counter, docs, issue_urls, patched_file_types_list,
                                hdbscan_min_cluster_size=min_size,
                                hdbscan_min_samples=min_samples,
                                dbscan_metric=metric,
                                dbscan_eps=eps,
                                representation_model=representation_model,
                                vectortizer_min_df=min_df,
                                vectortizer_max_df=max_df
                            )
                            num_all_topics = len(topic_model.get_topics())
                            print(f"Number of topics (including outliers): {num_all_topics}")
                            print(f"Silhouette Score: {sil_score}")
                            # Get top words per topic
                            topic_words = []
                            for topic_id in topic_model.get_topic_freq()["Topic"].values:
                                if topic_id == -1:
                                    continue
                                words = [word for word, _ in topic_model.get_topic(topic_id)]
                                topic_words.append(words)
                            
                            fdocs = results_df["text_for_topic_modeling"]
                            tokenized_docs = [simple_tokenize(doc) for doc in fdocs]
                            dictionary = Dictionary(tokenized_docs)
                            print(f"Length of tokenized_docs for coherence score: {len(tokenized_docs)}") 
                            # Save tokenized docs
                            with open(f"tokenized_docs_{counter}.json", "w") as f:
                                json.dump(tokenized_docs, f)
                            
                            # Save gensim dictionary
                            dictionary.save(f"dictionary_{counter}.dict")
                            coherence_model = CoherenceModel(
                                topics=topic_words,
                                texts=tokenized_docs,  # Not joined strings; list of tokens
                                dictionary=dictionary,   # dictionary mapping tokens to IDs
                                coherence='c_v',
                                topn=10
                            )
                            coherence_score = coherence_model.get_coherence()
                            print(f"Topic Coherence (C_v): {coherence_score:.3f}")
                            results.append({
                                "counter": counter,
                                "min_size": min_size,
                                "min_samples": min_samples,
                                "metric": metric,
                                "eps": eps,
                                "min_df": min_df,
                                "max_df": max_df,
                                "Silhouette Score": sil_score,
                                "Topic Coherence": coherence_score,
                                "Total Topics": num_all_topics
                            })
                            # save model
                            topic_model.save("bertopic_model_" + str(counter))
                            # --- Save results ---
                            tm_results_file = "topic_modeling_results_" + str(counter) + ".csv"
                            results_df.to_csv(tm_results_file, index=False)
                            print(f"Saved results to {tm_results_file}")
                            counter += 1
                        except ValueError as e:
                            print(f"Combination failed: min_size={min_size}, min_samples={min_samples}, eps={eps}, metric={metric}, error={str(e)}")



results_df = pd.DataFrame(results)
results_df.to_csv(results_file, index=False)
print(f"Saved results to {results_file}")
