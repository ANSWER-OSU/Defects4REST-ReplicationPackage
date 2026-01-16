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
import sys
import xml.etree.ElementTree as ET
import pandas as pd
import time
import json
import re
from openai import OpenAI

# Hardcode your API key here (replace YOUR_API_KEY with your actual key)
client = OpenAI(api_key="")

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
        return "other-file"


# the purpose of this method is to pre-process the title and description text 
# that is input to GPT. The logic of pre-processing includes general noise removal 
# and API-specific heuristics
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
            None
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

def classify_issue_with_gpt(prompt):
    for _ in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in software quality and REST APIs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            reply = response.choices[0].message.content.strip()
            data = json.loads(reply)
            label = data.get("label", "").lower()
            confidence = float(data.get("confidence", 0.0))
            if label in ["bug", "no-bug"] and 0.0 <= confidence <= 1.0:
                return label, confidence
            else:
                print(f"Unexpected format: {reply}")
        except Exception as e:
            print(f"Error Prompting: {e}\nResponse: {locals().get('reply', '')}")
            time.sleep(2)
    return "no-bug", 0.0

input_dir = sys.argv[1]
rows = []

total_issues = 0

for filename in os.listdir(input_dir):
    if not filename.endswith(".xml"):
        continue
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


    combined_text = clean_text(f"{title}\n{desc}\n{' '.join(patched_file_types)}")
   

    gpt_prompt = (
        f"You are an expert in software quality and REST APIs.\n"
        f"A REST API defect refers to any observable failure or regression in the behavior of a RESTful system as visible to the client.\n"
        f"This includes:\n"
        f"- Incorrect HTTP status codes\n"
        f"- Malformed, incomplete, or inconsistent JSON responses\n"
        f"- Missing required parameters or fields\n"
        f"- Violations of documented API contracts or expected behaviors\n"
        f"- Incorrect data in successful response that violates factual correctness\n"
        f"- incorrect request construction, missing parameter support, or regressions that break previously valid inputs\n"
        f"- Backward-incompatible changes in input handling or return values\n"
        f"- Unsuccessful client-server communication because all requests fail\n"
        f"Given the following GitHub issue title, description, and modified file types, determine whether it describes a REST API defect.\n"
        f"Respond *only* with a JSON object exactly matching this format, with no extra text or code blocks:\n"
        f'{{"label": "bug" or "no-bug", "confidence": float between 0 and 1}}\n'
        f"Title: {title}\n"
        f"Description: {desc}\n"
        f"Patched File Types: {', '.join(set(patched_file_types))}\n"
    )

    print("##################### START #########################")
    print(gpt_prompt)
    label, confidence = classify_issue_with_gpt(gpt_prompt)
    print(label, confidence)
    print("##################### END #########################\n\n\n")

    rows.append({
        "issue_no": issue_no,
        "repo": repo,
        "issue_url": issue_url,
        "title": title,
        "description": desc,
        "patched_file_types": " | ".join(patched_file_types),
        "text_for_topic_modeling": combined_text,
        "prediction": label,
        "confidence": confidence
    })

df = pd.DataFrame(rows)
df.to_csv("all_issues_with_predictions.csv", index=False)

bug_df = df[(df["prediction"] == "bug") & (df["confidence"] >= 0.7)]
bug_df.to_csv("rest_api_issues.csv", index=False)

print("Total issues analyzed:", total_issues)
print("Saved all issues to: all_issues_with_predictions.csv")
print("Saved high-confidence bugs to: rest_api_issues.csv ({len(bug_df)} entries)")

