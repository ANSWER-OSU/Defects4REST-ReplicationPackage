import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from collections import defaultdict

# Step 1: Read defect list
defects_df = pd.read_csv("607_defects_types.csv", sep='\t')

# Base folder for XML files
base_folder = Path('../../../rest-taxonomy-study/data/mined_issues')

# Function to parse fix time from XML
def get_timediff_from_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        td_elem = root.find('TIMEDIFFERENCEDAYS')
        if td_elem is not None and td_elem.text.isdigit():
            td_val = int(td_elem.text)
            if td_val > 365:
                print(f"Long time to fix (>1yr): {xml_path} => {td_val}")
            return td_val
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
    return None

# Step 2: Aggregate fix times by defect type
defect_to_durations = defaultdict(list)

for _, row in defects_df.iterrows():
    issue_no = row['issue_no']
    repo = row['repo']
    defect_type = row['defect type']

    xml_file = base_folder / repo / f"{repo}_Issue{issue_no}.xml"
    if not xml_file.exists():
        print(f"Missing: {xml_file}")
        continue

    td = get_timediff_from_xml(xml_file)
    if td is not None:
        defect_to_durations[defect_type].append(td)

# Step 3: Compute stats
results = []

for defect_type, durations in defect_to_durations.items():
    if durations:
        stats = {
            "defect_type": defect_type,
            "count": len(durations),
            "min": np.min(durations),
            "max": np.max(durations),
            "mean": np.mean(durations),
            "stdev": np.std(durations, ddof=1) if len(durations) > 1 else 0.0
        }
        results.append(stats)

# Step 4: Save and show
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="mean", ascending=False)
results_df.to_csv('defect_type_time_stats.csv', index=False)

print(results_df)
