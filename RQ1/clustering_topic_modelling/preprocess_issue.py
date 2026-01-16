# the purpose of this script is to take as input the "text_for_topic_modeling" 
# as input from the rest_api_defects.csv file generated for an API and preprocess 
# the text by: 
# - removing numbers, symbols, punctuations, HTTP links, parenthesis, etc. 
# - tokenizing the text considering camelCase splitting 
# - converting everything into lower case 
# - removing stopwords and commonly-occuring words

import pandas as pd
import re
import nltk
import sys
import string
from nltk.corpus import stopwords, wordnet

# Load the CSV data
api = sys.argv[1]  # e.g., Annif
df = pd.read_csv(sys.argv[2])  # e.g., rest_api_issues.csv

# Basic English stopwords + domain-specific
stop_words = set(stopwords.words('english')).union(set([
    'commit', 'debug', 'fix', 'source', 'coauthoredby', 'merge', 'pull', 'request',
    'update', 'add', 'remove', 'line', 'file', 'author', 'version', 'build', 'test',
    'code', 'change', 'issue', 'error', 'problem', 'try', 'run', 'using',
    'chore', 'feat', 'doc', 'hotfix', 'support', "sun", "mon", "tue", "wed", "thu", 
    "fri", "sat", "master", "info", "dev", "main", "release", "v1", "v2", "patch",
    "Annif", "apistar", "awx", "catwatch", "cgm-remote-monitor", "cwa-verification-server", 
    "digdag", "djoser", "dolibarr", "DSpace", "elassandra", "elasticsearch", "envirocar-server",
    "flowable-engine", "ghost", "granary", "harness", "hummingbot", "hydrus", "kafka-rest",
    "label-studio", "localsend", "management-api-for-apache-cassandra", "mastodon",
    "mobile-security-framework-mobsf", "modular-monolith-with-ddd", "mygpo", "netbox",
    "nocodb", "nopcommerce", "OrchardCore", "outline-server", "plane", "podman", "redash",
    "refugerestrooms", "restcountries", "seaweedfs", "shopizer", "signal-cli-rest-api",
    "silver", "SpaceX-API", "spring-petclinic-rest", "stf", "strapi", "supabase", "traefik",
    "uptime-kuma", "vercel", "WP-API", "zuul"
]))

def preprocess_text(text):
    if pd.isna(text):
        return []

    # Lowercase and clean
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\b[\w.-]+_[\w.-]+\b', ' ', text)

    # Remove HTTP and markdown-style links
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)

    # Remove code blocks (```...```)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Remove inline code (`...`)
    text = re.sub(r'`[^`]*`', '', text)

    # remove 1-2 letter tokens like 'js', 'py'
    text = re.sub(r"\b[a-zA-Z]{1,2}\b", "", text)  

    # Remove file paths and file extensions
    text = re.sub(r"\b(src|usr|bin|org|com|net|lib|tat|xc|js|ts|py|java|cpp)\b", "", text)
    text = re.sub(r"\b\w+\.(js|py|ts|java|html|json|xml)\b", "", text)

    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)   # camelCase -> camel Case
    text = text.replace('_', ' ').replace('-', ' ')    # snake_case and kebab-case
    
    text_tokens = text.split()
    tokens = [t for t in text_tokens if t not in stop_words and len(t) > 2]
    text = ' '.join(tokens)

    return text

# Fill NaNs and concatenate title + description
df["combined_text"] = df["title"].fillna("") + " " + df["description"].fillna("")

# Preprocess the combined text
df["text_for_topic_modeling"] = df["combined_text"].apply(preprocess_text)

# Save
df.to_csv("preprocessed_rest_api_issue_" + api + ".csv", index=False)
print("Preprocessed text saved to 'preprocessed_rest_api_issue_" + api + ".csv'")

