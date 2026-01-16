import pandas as pd

# Load the original CSV
df = pd.read_csv("defect_sheet.csv", encoding="cp1252")  # <-- change filename if needed

# Count occurrences of each Sub Defect Type
counts = df["defect type"].value_counts().reset_index()
counts.columns = ["Sub Defect Type", "#Defects"]

# Mapping from Sub Defect → Main Defect
sub_to_main = {
    "Container and Resource Quota Handling Errors": "Configuration and Environment Issues (T1)",
    "Job Execution and Workflow Configuration Defects": "Configuration and Environment Issues (T1)",
    "Environment-Specific Behavior and Configuration Bugs": "Configuration and Environment Issues (T1)",
    
    "Schema and Payload Validation Errors in POST APIs": "Data Validation and Query Processing Errors (T2)",
    "Query Filter and Search Parameter Handling Errors": "Data Validation and Query Processing Errors (T2)",
    
    "Authentication and Token Management Errors": "Authentication, Authorization, and Session Management Issues (T3)",
    "Session, Token, and Account Lifecycle Management Errors": "Authentication, Authorization, and Session Management Issues (T3)",
    
    "Middleware Integration Failures in REST APIs": "Integration, Middleware, and Runtime Environment Failures (T4)",
    "Process Signal and Grouping Issues in Containerized APIs": "Integration, Middleware, and Runtime Environment Failures (T4)",
    "Runtime and Dependency Errors": "Integration, Middleware, and Runtime Environment Failures (T4)",
    
    "Volume and File Upload/Access Errors": "Data Storage, Access, and Volume Errors (T5)",
    "Database/Table User Access Handling Errors": "Data Storage, Access, and Volume Errors (T5)",
    
    "Index and Cluster Coordination Failures": "Distributed Systems and Clustering Failures (T6)"
}

# Add Main Defect Type column
counts["Defect Type"] = counts["Sub Defect Type"].map(sub_to_main)

# Reorder columns: Main Defect Type, Sub Defect Type, #Defects
counts = counts[["Defect Type", "Sub Defect Type", "#Defects"]]

# Sort nicely
counts = counts.sort_values(by=["Defect Type", "Sub Defect Type"]).reset_index(drop=True)

# Print final table
print(counts.to_string(index=False))

# Save final table to CSV
counts.to_csv("defect_main_sub_counts.csv", index=False)
