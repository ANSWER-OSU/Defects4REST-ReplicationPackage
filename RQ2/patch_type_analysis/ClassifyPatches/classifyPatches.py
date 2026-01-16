import os
import sys
import xml.etree.ElementTree as ET
import pandas as pd
import time
import json
import re
import csv

def classify_file_type(filename):
    filename = filename.lower()
    if "test" in filename or filename.endswith(("_test.java", "_test.py", "spec.js", "test.js")):
        return "test-file" 
    elif filename.endswith((".md", ".rst", ".yaml", ".json", ",adoc", ".markdown")) or ("readme" in filename or "changelog" in filename):
        return "documentation-file"
    elif filename.endswith((".json", ".yaml", ".yml", ".xml", ".csv", ".po", ".lang")) or ("data" in filename or "dataset" in filename or "resources" in filename):
        return "data-file"
    elif filename.endswith((".yml", ".yaml", ".json", ".xml", ".properties", ".conf", ".sh", ".in", ".j2", ".toml", ".sln", ".csproj", ".props", ".cfg")) or any(ext in filename for ext in ("mvn", "gradle", "pom.xml", "build.gradle", "docker-compose", "helm", "requirements", "makefile", "config", "go.mod", "go.sum", "yarn.lock", "nuget.config")):
        return "config-file"
    elif filename.endswith((".java", ".py", ".js", ".jsx", ".ts", ".cpp", ".c", ".go", ".rb", ".cs", ".h", ".php", ".proto", ".tsx")):
        return "source-file"
    elif filename.endswith((".sql", ".db", ".sqlite", ".psql")):
        return "database-file"
    elif "dockerfile" in filename:
        return "container-file"
    elif filename.endswith((".html", ".css", ".scss", ".png", ".svg", ".woff", ".less", ".ttf", ".eot", ".cshtml", ".vue", ".hbs")):
        return "ui-file"
    else:
        print("WHAT TYPE OF FILE IS THIS: ", filename)
        return "other-file"

input_dir = sys.argv[1]
rest_api_issues_csv = sys.argv[2]
rows = []
total_issues = 0
issue_numbers = []

def get_issue_numbers(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            issue_no = row.get('issue_no')
            if issue_no:
                issue_numbers.append(issue_no)
    print("total rest api issues found: ", len(issue_numbers))
    print(issue_numbers)
    return issue_numbers

def clean_text(text):
    # Extract the text between the two markers for yt-dlp API 
    # Define ordered list of possible marker pairs
    marker_patterns = [
        (
            r"### Provide a description that is worded well enough to be understood",
            r"### Provide verbose output that clearly demonstrates the problem"
        ),
        (
            r"### Description",
            r"### Verbose log"
        ),
        (
            r"## Description",
            None  # This means capture from this marker to the end
        )
    ]

    for start_marker, end_marker in marker_patterns:
        if end_marker:
            pattern = rf"{start_marker}(.*?){end_marker}"
        else:
            pattern = rf"{start_marker}(.*)"  # Capture everything after the start marker

        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1)
            break

    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Remove sequences of 3 or more repeated non-alphanumeric, non-whitespace chars anywhere in text
    text = re.sub(r'([^\w\s])\1{2,}', '', text)
    # Flatten multiline text into a single line
    return " ".join(text.splitlines()).strip()


issue_numbers = get_issue_numbers(rest_api_issues_csv)
issue_numbers = set(str(num) for num in issue_numbers)


for filename in os.listdir(input_dir):
    if not filename.endswith(".xml"):
        continue
    match = re.match(r".*Issue(\d+)\.xml$", filename)
    if match:
        issue_no = match.group(1)
        if issue_no not in issue_numbers:
            continue
    
    print(f"Processing file: {filename}")
    total_issues = total_issues + 1
    tree = ET.parse(os.path.join(input_dir, filename))
    root = tree.getroot()

    title = clean_text(root.findtext("TITLE", default=""))
    desc = clean_text(root.findtext("DESCRIPTION", default=""))
    issue_url = clean_text(root.findtext("ISSUEURL", default=""))
    repo = clean_text(root.findtext("REPONAME", default=""))
    issue_no = clean_text(root.findtext("ISSUENO", default=""))

    buggy_msg = root.find("BUGGYCOMMIT/MESSAGE")
    buggy_msg_text = clean_text(buggy_msg.text if buggy_msg is not None else "")

    patch_msgs, patched_files, patched_file_types = [], [], []
    for commit in root.findall("PATCHCOMMITS/COMMIT"):
        msg = clean_text(commit.findtext("MESSAGE", default=""))
        patch_msgs.append(msg)
        for file_elem in commit.findall("PATCHEDFILES/FILE"):
            file_path = clean_text(file_elem.text or "")
            patched_files.append(file_path)
            patched_file_types.append(classify_file_type(file_path))

    rows.append({
        "issue_no": issue_no,
        "repo": repo,
        "issue_url": issue_url,
        "title": title,
        "description": desc,
        "patched_file_types": " | ".join(list(set(patched_file_types))),
    })

df = pd.DataFrame(rows)
df.to_csv("rest_api_issues_with_patchtyes.csv", index=False)
print("Total issues analyzed:", total_issues)
print(f"\n✅ Saved all issues to: rest_api_issues_with_patchtyes.csv")

