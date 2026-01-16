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
import matplotlib.pyplot as plt
import numpy as np
import sys

# Load CSV file
df = pd.read_csv(sys.argv[1])

print("total congiurations tried:", len(df))
# Filter rows where Total Topics >= 10
df = df[df["Total Topics"] >= 11]

print("configurations with topics >= 10:", len(df))

# Normalize metrics for Pareto computation
df["Silhouette_norm"] = (df["Silhouette Score"] - df["Silhouette Score"].min()) / (df["Silhouette Score"].max() - df["Silhouette Score"].min())
df["Coherence_norm"] = (df["Topic Coherence"] - df["Topic Coherence"].min()) / (df["Topic Coherence"].max() - df["Topic Coherence"].min())

# Pareto front computation
def is_dominated(row, others):
    return any(
        (other["Silhouette_norm"] >= row["Silhouette_norm"]) and
        (other["Coherence_norm"] >= row["Coherence_norm"]) and
        ((other["Silhouette_norm"] > row["Silhouette_norm"]) or
         (other["Coherence_norm"] > row["Coherence_norm"]))
        for _, other in others.iterrows()
    )

pareto = df[~df.apply(lambda row: is_dominated(row, df.drop(index=row.name)), axis=1)].copy()

# Combined score for ranking
pareto["combined_score"] = pareto["Silhouette Score"] + pareto["Topic Coherence"]
top_5 = pareto.sort_values(by="combined_score", ascending=False).head(10)

# Print top 5 configs on terminal
print("\nTop 5 Configurations (by Silhouette + Coherence):")
print(top_5.drop(columns=["Silhouette_norm", "Coherence_norm", "combined_score"]).to_string(index=False))

# Plot all points
plt.figure(figsize=(10, 7))
plt.scatter(df["Silhouette Score"], df["Topic Coherence"], label="All Configurations", alpha=0.4)

# Highlight Pareto front points
plt.scatter(pareto["Silhouette Score"], pareto["Topic Coherence"], color='red', label="Pareto Front", s=60)

# Annotate top 5 configs on the Pareto front
config_count = 0
for _, row in pareto.iterrows():
    plt.annotate(
        f'#{row.name}',
        (row["Silhouette Score"], row["Topic Coherence"]),
        textcoords="offset points",
        xytext=(5,-5),
        ha='left',
        fontsize=12,
        fontweight='bold',
        color='darkblue'
    )
    config_count += 1

print(f"Total configs plotted:{config_count}")

#plt.title("Hyperparameter Tuning: Silhouette Score vs Topic Coherence")
plt.xlabel("Silhouette Score", fontsize=14)
plt.ylabel("Topic Coherence (C_v)", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
plt.grid(True)
plt.tight_layout()
# Save the figure
plt.savefig("pareto_front.png", dpi=300)
plt.show()

