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

import pandas as pd

# Load the original CSV
df = pd.read_csv("defect_sheet.csv", encoding="cp1252")  # <-- change filename if needed

# Mapping from Sub Defect → Main Defect
sub_to_main = {
    "Container and Resource Quota Handling Errors": "Configuration and Environment Issues",
    "Job Execution and Workflow Configuration Defects": "Configuration and Environment Issues",
    "Environment-Specific Behavior and Configuration Bugs": "Configuration and Environment Issues",
    
    "Schema and Payload Validation Errors in POST APIs": "Data Validation and Query Processing Errors",
    "Query Filter and Search Parameter Handling Errors": "Data Validation and Query Processing Errors",
    
    "Authentication and Token Management Errors": "Authentication, Authorization, and Session Management Issues",
    "Session, Token, and Account Lifecycle Management Errors": "Authentication, Authorization, and Session Management Issues",
    
    "Middleware Integration Failures in REST APIs": "Integration, Middleware, and Runtime Environment Failures",
    "Process Signal and Grouping Issues in Containerized APIs": "Integration, Middleware, and Runtime Environment Failures",
    "Runtime and Dependency Errors": "Integration, Middleware, and Runtime Environment Failures",
    
    "Volume and File Upload/Access Errors": "Data Storage, Access, and Volume Errors",
    "Database/Table User Access Handling Errors": "Data Storage, Access, and Volume Errors",
    
    "Index and Cluster Coordination Failures": "Distributed Systems and Clustering Failures"
}

# Map each sub-defect to main defect
df["Defect Type"] = df["defect type"].map(sub_to_main)

# Aggregate counts by Main Defect Type
main_counts = df["Defect Type"].value_counts().reset_index()
main_counts.columns = ["Defect Type", "#Defects"]

# Sort by count descending
main_counts = main_counts.sort_values(by="#Defects", ascending=False).reset_index(drop=True)

# Add ranking with ties handled using "dense" 
main_counts["Rank"] = main_counts["#Defects"].rank(method='dense', ascending=False).astype(int)

# Reorder columns
main_counts = main_counts[["Rank", "Defect Type", "#Defects"]]

# Print final table
print(main_counts.to_string(index=False))

# Print total row
total = main_counts["#Defects"].sum()
print(f"\ntotal {total}")

# Save final table to CSV
main_counts.to_csv("defect_main_counts.csv", index=False)
