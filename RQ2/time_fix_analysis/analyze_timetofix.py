import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from collections import defaultdict

# Step 1: Read defect list
defects_df = pd.read_csv("607_defects_types.csv", sep="\t")

# Base folder for XML files
base_folder = Path(
    "/home/d/Defects4REST-Artifact/RQ1/issue_mining/result_mined_issues/issues_xml"
)

# Function to parse fix time from XML
def get_timediff_from_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        td_elem = root.find("TIMEDIFFERENCEDAYS")

        if td_elem is not None and td_elem.text and td_elem.text.isdigit():
            return int(td_elem.text)

    except Exception:
        pass  

    return None

# Step 2: Aggregate fix times by defect type
defect_to_durations = defaultdict(list)

for _, row in defects_df.iterrows():
    issue_no = row["issue_no"]
    repo = row["repo"]
    defect_type = row["defect type"]

    xml_file = base_folder / repo / f"{repo}_Issue{issue_no}.xml"
    if not xml_file.exists():
        continue  

    td = get_timediff_from_xml(xml_file)
    if td is not None:
        defect_to_durations[defect_type].append(td)

# Step 3: Compute stats
results = []

for defect_type, durations in defect_to_durations.items():
    if durations:
        results.append({
            "defect_type": defect_type,
            "count": len(durations),
            "min": np.min(durations),
            "max": np.max(durations),
            "mean": round(np.mean(durations), 2),
            "stdev": round(np.std(durations, ddof=1), 2) if len(durations) > 1 else 0.00
        })

# Step 4: Save and show
results_df = pd.DataFrame(results).sort_values(by="mean", ascending=False)
results_df.to_csv("defect_type_time_stats.csv", index=False)
pd.options.display.float_format = "{:.2f}".format
print(results_df.drop(columns=["count"]))
