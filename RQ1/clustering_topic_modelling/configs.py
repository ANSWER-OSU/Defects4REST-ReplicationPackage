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

# Selected single-run top 5 configurations

CONFIG_ID = 180    #  Change this value to run a different configuration


CONFIGS = {
   
    344: {
        "min_cluster_size": 30,
        "min_samples": 10,
        "metric": "cosine",
        "eps": 0.5,
        "min_df": 2,
        "max_df": 300,
    },

    519: {
        "min_cluster_size": 40,
        "min_samples": 10,
        "metric": "cosine",
        "eps": 0.5,
        "min_df": 2,
        "max_df": 500,
    },

    517: {
        "min_cluster_size": 40,
        "min_samples": 10,
        "metric": "cosine",
        "eps": 0.5,
        "min_df": 2,
        "max_df": 300,
    },

    180: {
        "min_cluster_size": 20,
        "min_samples": 10,
        "metric": "cosine",
        "eps": 0.5,
        "min_df": 3,
        "max_df": 600,
    },

    583: {
        "min_cluster_size": 40,
        "min_samples": 20,
        "metric": "cosine",
        "eps": 0.5,
        "min_df": 3,
        "max_df": 400,
    },
}
