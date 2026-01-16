import pandas as pd
import os
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

# --- Step 1: Read Main Defect File ---
defects_df = pd.read_csv("607_defects_types.csv", sep='\t')

# --- Step 2: Aggregate patched_file_types per defect type ---
defect_to_patchtype_counter = defaultdict(Counter)

for _, row in defects_df.iterrows():
    issue_no = row['issue_no']
    repo = row['repo']
    defect_type = row['defect type']

    patch_csv_path = f"ClassifyPatches/rest_api_issues_with_patchtyes_{repo}.csv"
    if not os.path.isfile(patch_csv_path):
        continue

    try:
        patch_df = pd.read_csv(patch_csv_path)
        patch_row = patch_df[patch_df['issue_no'] == issue_no]

        if patch_row.empty or pd.isna(patch_row.iloc[0]['patched_file_types']):
            continue

        patched_types = patch_row.iloc[0]['patched_file_types']
        normalized_types = set(t.strip().lower() for t in patched_types.split('|') if t.strip())

        for ptype in normalized_types:
            defect_to_patchtype_counter[defect_type][ptype] += 1

    except Exception as e:
        print(f"Error with {patch_csv_path} or issue {issue_no}: {e}")

# --- Step 3: Print Summary ---
for defect_type, counter in defect_to_patchtype_counter.items():
    total = sum(counter.values())
    print(f"{defect_type} {total} {dict(counter)}")

# --- Step 4: Prepare DataFrame for Plot ---
# Get full list of file types
all_file_types = sorted({ftype for counter in defect_to_patchtype_counter.values() for ftype in counter})

# Create ordered list of defect types (ST1, ST2, ..., ST13)
unique_defect_types = sorted(defect_to_patchtype_counter.keys())
defect_type_to_label = {dt: f"ST{i+1}" for i, dt in enumerate(unique_defect_types)}
label_to_defect_type = {v: k for k, v in defect_type_to_label.items()}

# Build a DataFrame
data = []
index = []

for defect_type in unique_defect_types:
    label = defect_type_to_label[defect_type]
    index.append(label)
    counter = defect_to_patchtype_counter[defect_type]
    row = [counter.get(ftype, 0) for ftype in all_file_types]
    data.append(row)

agg_df = pd.DataFrame(data, index=index, columns=all_file_types)

# Normalize per row (per defect type)
agg_df_norm = agg_df.div(agg_df.sum(axis=1), axis=0).fillna(0)

# --- Step 5: Plot Stacked Bar Chart ---
plt.figure(figsize=(14, 8))
agg_df_norm.plot(kind='bar', stacked=True, colormap='tab20', width=0.7)

# Customize labels
plt.xlabel('Defect Type')
plt.ylabel('Fraction of Patched File Type')
#plt.xticks(rotation=45)
plt.legend(title='Patched File Types', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("patched_file_types_stacked_bar.png", dpi=300)
plt.close()

