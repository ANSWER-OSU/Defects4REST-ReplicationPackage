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

import os
import csv
import requests
import argparse
import xml.etree.ElementTree as ET
import xml.dom.minidom
import logging
from datetime import datetime
import sys
import time
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GitHubIssueProcessor:
    def __init__(self, owner, repo, github_auth_token, resultpath):
        self.owner = owner
        self.repo = repo
        self.github_auth_token = github_auth_token
        self.base_dir = os.path.join(resultpath, "issues_xml", repo)
        self.master_csv_path = os.path.join(self.base_dir, f"AAAmastertracker_{repo}.csv")

        self.checkpoints_dir = os.path.join(os.getcwd(), "checkpoints")
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        self.checkpoint_file = os.path.join(self.checkpoints_dir, f"{repo}.txt")

        self.github_api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        self.headers = {"Authorization": f"token {self.github_auth_token}"}
        os.makedirs(self.base_dir, exist_ok=True)

    def sanitize_xml_text(self, text):
        if not text:
            return ''
        text = re.sub(r'[^\x09\x0A\x0D\x20-\x7F\x85\xA0-\uD7FF\uE000-\uFFFD]', '', text)
        return ' '.join(text.split())

    def make_github_request(self, url, params=None, headers=None):
        if headers is None:
            headers = self.headers
        if params is None:
            params = {}

        while True:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code in (403, 429):
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 600))
                reset_timestamp = datetime.utcfromtimestamp(reset_time)
                sleep_duration = (reset_timestamp - datetime.utcnow()).total_seconds() + 10
                logger.warning(f"Rate limit or forbidden error. Sleeping for {sleep_duration:.2f} seconds until {reset_timestamp}.")

                with open(self.checkpoint_file, "w") as f:
                    f.write(str(params.get("page", 1)))

                time.sleep(sleep_duration)
            else:
                return response

    def fetch_closed_issues(self, checkpoint=None):
        issues = []
        page = checkpoint if checkpoint else 1
        while True:
            response = self.make_github_request(
                self.github_api_url,
                params={"state": "closed", "per_page": 100, "page": page}
            )
            logger.info(f"Fetching page {page}")

            if response.status_code != 200:
                logger.error(f"Error fetching issues: {response.status_code} {response.text}")
                break

            data = response.json()
            if not data:
                break

            filtered_issues = [issue for issue in data if "pull_request" not in issue]
            issues.extend(filtered_issues)

            page += 1

        return issues

    def fetch_modified_files_and_commits(self, issue_number):
        timeline_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{issue_number}/timeline"
        response = self.make_github_request(
            timeline_url,
            headers={**self.headers, "Accept": "application/vnd.github.mockingbird-preview"}
        )

        if response.status_code != 200:
            logger.error(f"Error fetching timeline for issue #{issue_number}: {response.status_code} {response.text}")
            return [], []

        timeline_data = response.json()
        commit_shas = []

        for event in timeline_data:
            if event.get("event") == "referenced" and "commit_id" in event:
                commit_shas.append(event["commit_id"])

        patched_commits = []

        for sha in commit_shas:
            commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{sha}"
            commit_response = self.make_github_request(commit_url)
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                patched_commits.append({
                    "sha": sha,
                    "message": self.sanitize_xml_text(commit_data.get("commit", {}).get("message", "")),
                    "files": [self.sanitize_xml_text(file["filename"]) for file in commit_data.get("files", [])]
                })

        buggy_commit = None
        if patched_commits:
            first_sha = patched_commits[0]["sha"]
            commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{first_sha}"
            commit_response = self.make_github_request(commit_url)
            if commit_response.status_code == 200:
                parents = commit_response.json().get("parents", [])
                if parents:
                    parent_sha = parents[0].get("sha")
                    parent_commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{parent_sha}"
                    parent_commit_response = self.make_github_request(parent_commit_url)
                    if parent_commit_response.status_code == 200:
                        parent_data = parent_commit_response.json()
                        buggy_commit = {
                            "sha": parent_sha,
                            "message": self.sanitize_xml_text(parent_data.get("commit", {}).get("message", ""))
                        }

        return patched_commits, buggy_commit

    def compute_time_difference(self, issue_created_at, issue_closed_at):
        if not issue_created_at or not issue_closed_at:
            return "Not available"
        created_dt = datetime.strptime(issue_created_at, "%Y-%m-%dT%H:%M:%SZ")
        closed_dt = datetime.strptime(issue_closed_at, "%Y-%m-%dT%H:%M:%SZ")
        return str((closed_dt - created_dt).days)

    def create_issue_xml(self, issue):
        issue_number = issue['number']
        title = self.sanitize_xml_text(issue['title'])
        description = self.sanitize_xml_text(issue.get('body', 'No Description'))
        issue_url = issue['html_url']
        repo_name = self.repo
        created_at = issue.get('created_at', None)
        closed_at = issue.get('closed_at', None)
        patched_commits, buggy_commit = self.fetch_modified_files_and_commits(issue_number)

        if not patched_commits:
            logger.info(f"Skipping issue #{issue_number}: no commit attached.")
            return None, None

        root = ET.Element("ISSUE")
        ET.SubElement(root, "ISSUENO").text = str(issue_number)
        ET.SubElement(root, "ISSUEURL").text = issue_url
        ET.SubElement(root, "TITLE").text = title
        ET.SubElement(root, "DESCRIPTION").text = description
        ET.SubElement(root, "REPONAME").text = repo_name

        time_diff = self.compute_time_difference(created_at, closed_at)
        ET.SubElement(root, "TIMEDIFFERENCEDAYS").text = time_diff

        if buggy_commit:
            buggy = ET.SubElement(root, "BUGGYCOMMIT")
            
            ET.SubElement(buggy, "MESSAGE").text = buggy_commit["message"]
            ET.SubElement(buggy, "SHA").text = buggy_commit["sha"]

        patch = ET.SubElement(root, "PATCHCOMMITS")
        for commit in patched_commits:
            commit_elem = ET.SubElement(patch, "COMMIT")
            ET.SubElement(commit_elem, "MESSAGE").text = commit["message"]
            ET.SubElement(commit_elem, "SHA").text = commit["sha"]
            patched_files_elem = ET.SubElement(commit_elem, "PATCHEDFILES")
            for file in commit["files"]:
                ET.SubElement(patched_files_elem, "FILE").text = file

        pretty_xml = xml.dom.minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")
        xml_filename = f"{repo_name}_Issue{issue_number}.xml"
        xml_filepath = os.path.join(self.base_dir, xml_filename)

        with open(xml_filepath, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        return xml_filename, issue_url

    def update_master_csv(self, entries):
        file_exists = os.path.isfile(self.master_csv_path)
        with open(self.master_csv_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["XML File Name", "Issue URL"])
            writer.writerows(entries)

    def process_issues(self):
        checkpoint = None
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r") as f:
                content = f.read().strip()
                if content:
                    checkpoint = int(content)
                    logger.info(f"Resuming from checkpoint: Page {checkpoint}")
                else:
                    logger.info("Checkpoint file is empty. Starting from page 1.")
        else:
            logger.info("No checkpoint file found. Starting fresh.")

        closed_issues = self.fetch_closed_issues(checkpoint)
        entries = []

        for issue in closed_issues:
            xml_filename, issue_url = self.create_issue_xml(issue)
            if xml_filename and issue_url:
                entries.append([xml_filename, issue_url])

        if entries:
            self.update_master_csv(entries)
            logger.info(f"Processed {len(entries)} issues with XML reports. Output: {self.base_dir}")
        else:
            logger.warning("No qualifying issues (with commits/PRs) found.")

        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            logger.info("Checkpoint file removed after successful run.")

def main():
    parser = argparse.ArgumentParser(description="Process GitHub issues for a repository.")
    parser.add_argument('--repo-url', type=str, required=True, help='GitHub repository URL')
    parser.add_argument('--token', type=str, required=True, help='GitHub personal access token')
    parser.add_argument('--resultpath', type=str, required=True, help='Path of the root folder')

    args = parser.parse_args()

    parts = args.repo_url.replace("https://github.com/", "").strip().split('/')
    if len(parts) < 2:
        logger.error("Invalid GitHub repository URL.")
        return

    owner, repo = parts[0], parts[1].replace('.git', '')
    processor = GitHubIssueProcessor(owner, repo, args.token, args.resultpath)
    processor.process_issues()

if __name__ == "__main__":
    logger.info("ScriptStarted")
    main()
    logger.info("Script ended")

