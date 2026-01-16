import csv
import sys

rest_issues_csv_path = sys.argv[1]

def find_heterogeneous_issues(csv_path):
    heterogeneous_issues = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            patched_types_str = row['patched_file_types'].strip()
            patched_types = [pt.strip() for pt in patched_types_str.split('|') if pt.strip()]
            
            filtered_types = [pt for pt in patched_types if pt != 'test-file' and pt!= 'documentation-file']

            if len(set(filtered_types)) > 1:
                heterogeneous_issues.append((row['issue_url'], filtered_types))

    return heterogeneous_issues

results = find_heterogeneous_issues(rest_issues_csv_path)
for url, file_types in results:
    print(f"Issue URL: {url}")
    print(f"Patched file types: {file_types}")
    print("-" * 40)


