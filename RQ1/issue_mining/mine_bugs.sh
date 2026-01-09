#!/bin/bash
#SBATCH -c 4                         
#SBATCH -p dgx2                     
#SBATCH -J API_NAME
#SBATCH --output=slurm_API_NAME.out
#SBATCH --error=slurm_API_NAME.err
#SBATCH --time=7-00:00:00


# Check if an argument was provided
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <API URL> <GitHub token> <Root dir>"
    exit 1
fi

REPO_URL=$1
GITHUB_TOKEN=$2
ROOT_DIR=$3

python3 github_issue_processor.py --repo-url "$REPO_URL" --token "$GITHUB_TOKEN" --resultpath "$ROOT_DIR"

