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

import matplotlib.pyplot as plt
import numpy as np

# Paste your full data list here
confidence_values = [85, 80, 90, 90, 90, 90, 85, 80, 80, 90, 90, 90, 90, 90, 90, 90, 90, 90, 85, 90, 90, 80, 90, 90, 90, 90, 90, 90, 90, 85, 90, 85, 90, 90, 85, 90, 95, 90, 90, 90, 90, 80, 70, 80, 90, 90, 85, 80, 90, 90, 95, 90, 90, 90, 95, 90, 90, 90, 90, 95, 95, 90, 90, 90, 95, 90, 90, 90, 90, 90, 90, 95, 90, 80, 80, 85, 85, 90, 95, 90, 85, 90, 90, 90, 90, 90, 90, 80, 90, 90, 90, 90, 90, 90, 95, 85, 90, 90, 90, 85, 90, 90, 85, 90, 90, 90, 85, 90, 90, 95, 90, 95, 90, 90, 85, 85, 90, 95, 85, 95, 90, 90, 95, 95, 85, 90, 90, 90, 90, 90, 90, 95, 90, 95, 90, 80, 95, 90, 90, 90, 85, 95, 95, 80, 95, 95, 90, 80, 90, 95, 95, 85, 90, 90, 95, 95, 90, 90, 90, 90, 95, 85, 90, 90, 95, 85, 90, 90, 95, 90, 90, 90, 90, 90, 90, 90, 85, 90, 95, 90, 90, 90, 95, 85, 95, 95, 80, 90, 90, 90, 90, 95, 95, 95, 90, 90, 90, 90, 90, 90, 90, 85, 95, 85, 95, 90, 95, 95, 90, 80, 90, 85, 85, 90, 90, 95, 90, 85, 90, 85, 90, 95, 85, 85, 85, 85, 85, 85, 85, 85, 90, 90, 90, 90, 95, 95, 90, 90, 90, 90, 95, 95, 90, 95, 95, 85, 85, 95, 90, 85, 90, 85, 90, 90, 80, 90, 90, 85, 90, 95, 90, 95, 90, 90, 95, 90, 95, 95, 95, 90, 90, 95, 95, 90, 90, 95, 90, 95, 95, 85, 90, 90, 95, 95, 95, 95, 80, 90, 85, 90, 90, 90, 95, 95, 90, 90, 95, 90, 85, 90, 85, 85, 85, 85, 90, 85, 85, 80, 90, 90, 90, 85, 90, 95, 80, 85, 90, 85, 85, 90, 85, 90, 90, 85, 85, 85, 90, 90, 85, 85, 95, 85, 90, 90, 85, 85, 90, 95, 85, 85, 90, 90, 85, 85, 95, 90, 95, 85, 90, 95, 90, 85, 90, 90, 85, 85, 85, 90, 90, 85, 80, 90, 90, 80, 85, 95, 90, 85, 95, 85, 90, 90, 80, 90, 90, 95, 90, 95, 90, 90, 90, 90, 90, 95, 95, 90, 90, 85, 95, 90, 95, 95, 90, 95, 90, 90, 85, 90, 85, 90, 85, 90, 95, 80, 90, 95, 95, 90, 95, 85, 85, 95, 80, 90, 95, 95, 90, 95, 95, 85, 95, 85, 90, 90, 95, 90, 90, 90, 95, 95, 95, 90, 90, 85, 90, 90, 85, 90, 90, 90, 90, 85, 90, 90, 85, 85, 90, 85, 85, 90, 85, 95, 90, 90, 95, 90, 90, 90, 90, 95, 85, 90, 90, 85, 95, 90, 90, 95, 90, 80, 90, 90, 90, 85, 85, 85, 95, 85, 95, 90, 85, 90, 90, 90, 85, 95, 90, 90, 85, 95, 85, 95, 85, 90, 90, 80, 90, 85, 90, 95, 85, 85, 90, 85, 85, 85, 85, 85, 80, 85, 85, 90, 90, 85, 80, 85, 90, 85, 90, 85, 90, 90, 85, 90, 80, 90, 90, 85, 85, 80, 90, 80, 85, 85, 85, 85, 85, 85, 95, 85, 85, 85, 90, 85, 85, 90, 90, 85, 85, 85, 85, 85, 90, 90, 80, 85, 85, 80, 90, 85, 90, 90, 95, 95, 90, 95, 85, 90, 85, 85, 90, 85, 90, 80, 90, 90, 95, 90, 90, 95, 95, 95, 95, 95, 95, 95, 95, 90, 85, 90, 95, 95, 95, 95, 95, 95, 95, 90, 95, 90, 90, 90, 95, 95, 95, 95, 95, 95, 95, 95, 95, 90, 95, 95, 95, 90, 95, 90, 90, 90, 90, 95, 95, 95, 90, 90, 95, 95, 95, 90, 90, 95, 90, 90, 95, 90, 95, 95, 95, 90, 90, 95, 95, 95, 80, 80, 85, 85, 85, 85, 85, 80, 85, 90, 90, 85, 80, 90, 85, 85, 90, 90, 95, 90, 85, 85, 85, 90, 85, 95, 95, 95, 90, 90, 95, 95, 90, 90, 90, 90, 85, 85, 85, 90, 90, 95, 85, 85, 95, 90, 85, 80, 90, 90, 90, 90, 85, 90, 90, 85, 90, 90, 85, 90, 90, 90, 70, 90, 85, 90, 85, 85, 90, 85, 95, 90, 90, 90, 90, 90, 90, 95, 95, 95, 90, 90, 85, 95, 90, 95, 90, 90, 90, 90, 90, 80, 95, 90, 90, 90, 95, 90, 95, 90, 90, 85, 90, 90, 95, 95, 90, 85, 95, 90, 95, 90, 90, 95, 90, 90, 90, 90, 85, 85, 85, 90, 90, 90, 80, 90, 95, 90, 95, 90, 90, 90, 95, 90, 90, 80, 90, 90, 95, 90, 90, 90, 90, 85, 90, 90, 90, 90, 90, 85, 95, 90, 90, 85, 90, 85, 90, 90, 85, 90, 90, 90, 85, 90, 85, 90, 95, 90, 95, 90, 90, 90, 90, 90, 90, 95, 95, 90, 95, 90, 95, 90, 90, 70, 95, 90, 90, 90, 90, 85, 95, 85, 90, 90, 90, 90, 95, 85, 90, 90, 90, 85, 85, 85, 90, 90, 85, 85, 85, 80, 90, 95, 85, 90, 90, 90, 85, 85, 90, 95, 85, 85, 90, 90, 90, 85, 80, 85, 90, 90, 90, 85, 85, 85, 90, 90, 90, 90, 90, 85, 85, 85, 85, 95, 95, 90, 85, 80, 90, 95, 85, 90, 90, 90, 90, 90, 90, 90, 95, 85, 90, 90, 90, 90]  


confidence = []

for c in confidence_values:
    confidence.append(c/100.0)


# Define bins from 70 to 100 with step size of 5
bins = np.arange(0.7, 1.00, 0.05)

# Plot histogram and get counts
plt.figure(figsize=(10, 6))
counts, bin_edges, _ = plt.hist(confidence, bins=bins, edgecolor='black', color='black')

# Add count labels on top of bars
for count, left, right in zip(counts, bin_edges[:-1], bin_edges[1:]):
    center = (left + right) / 2
    plt.text(center, count + 2, str(int(count)), ha='center', fontsize=15)

# Labels and formatting
plt.xlabel('confidence score', fontsize=16)
plt.ylabel('issues classified as REST API defects', fontsize=16)
#plt.title('Histogram of Confidence Scores')
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xticks(bins)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("histogram_confidence.pdf")
#plt.show()

# Verify sum of counts matches total data points
print("Sum of counts:", int(np.sum(counts)))
print("Total data points:", len(confidence_values))

