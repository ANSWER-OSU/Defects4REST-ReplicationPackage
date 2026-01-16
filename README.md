# Defects4REST Replication Package (ICSE 2026)

This is the artifact of the paper  **Defects4REST: A Benchmark of Real-World Defects to Enable Controlled Testing and Debugging Studies for REST API**, in Proceedings of the 48th International Conference on Software Engineering (ICSE), 2026 by Rahil P. Mehta, Pushpak Katkhede, and Manish Motwani. 

A copy of the accepted paper in pdf format is available at [defects4rest_icse26.pdf](https://github.com/ANSWER-OSU/Defects4REST-ReplicationPackage/blob/main/defects4rest_icse26.pdf). 

The link to the archival repository: https://doi.org/10.5281/zenodo.17607138

## Purpose

This artifact aims to facilitate the replication of the ICSE 2026 paper titled  **_Defects4REST: A Benchmark of Real-World Defects to Enable Controlled Testing and Debugging Studies for REST API_**, and help researchers to build on the work.


The artifact provides all code and data to replicate the results presented in our paper. To ease the replication, we organize the artifact in terms of the three research questions we address in the paper.

- **RQ1:** Common REST API Defect Types: This involves code and data related to mining closed issues along with associated commits and metadata (files modified and time to fix) from 51 REST-API-based GitHub projects (issue mining), classifying issues into REST-API defects and non-REST API defects (issue classification) and deriving defect taxonomy (clustering and topic modeling).

- **RQ2:** File Types Modified and Time to Resolve REST API Defects: This involves the code and data to analyze the types of developer-modified files in fixing the manually curated set of 607 REST API defects (patch file analysis), and the time it took developers to fix these defects (time to fix analysis).

- **RQ3:** Evaluating Current REST API Testing Tools Against Real-World Defects: This involves code and data to execute and analyze the results of four REST API testing techniques (EvoMaster, Schemathesis, RESTler, and AutoRestTest) on a 30-defect subset of Defects4REST.

### Badges Applied For

We are applying for the **Artifacts Available** and **Artifacts Reusable** badges.

**Artifacts Available:** We believe our artifact deserves the Artifacts Available badge because we make all the materials used to implement and replicate our study available on a publicly accessible archival repository.

**Artifacts Reusable:** We believe our artifact deserves the Artifacts Reusable badge because the materials we make available in our artifact can be reused by researchers and practitioners in various ways -- either to replicate our results or to augment or improve their own studies and technologies.

## Provenance

The virtual machine image (created using VirtualBox) to replicate the results is available at: 


## Data

The artifact consists of code, data, and execution logs. The total size of artifact is ~42 GB (uncompressed) and the VM requires ~30 GB; 


## Setup[]()

Please follow the following set of instructions to replicate our results. 

Note: The virtual machine was created and tested using VirtualBox version 7.2.4 on Ubuntu 24.04.03. Make sure you have atleast 30 GB of free storage to download and execute the virtual machine.

**Step 1.**  Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

**Step 2.**  Download virtual machine image  [Defects4REST.ova](Zenodo). Please note this is a large file (~30 GB) and may take some time (~20 min, depending on your Internet) to download.

**Step 3.**  Open VirtualBox.

**Step 4.**  Go to  `File`  >  `Import Appliance...`.

**Step 5.**  Find and select the downloaded virtual machine file  `Defects4REST.ova`. Click  `Continue`.

**Step 6.**  Click  `Agree`  in the Software License Agreement box.

**Step 7.**  Leave all the settings as they are and click  `Import`. (This will take around 6-10 minutes.)

Once the virtual machine is imported, it will appear in your VirtualBox Manager as  `Defects4REST`  as shown below.

![VBManager Screenshot](\Defects4REST-ReplicationPackage\images\VBManager.png)


You can now start the virtual machine by clicking the green  `Start`  arrow at the top of the VirtualBox Manager (see screenshot above).


#### Username and Password[]()
If you are asked for a password to login to the virtual machine (e.g., if the VM goes to sleep or you logged out and need to login), please use the password `defects123`.


When the machine boots up successfully you will see the screen as shown below.

![VBImage Screenshot](/Defects4REST-ReplicationPackage/images/VBImage.png)


## Usage

### How do I execute the artifact and replicate the published results?

Open a terminal window, change the working directory to  `/home/d/Defects4REST-Artifact`  (referred as  `Defects4REST-Artifact`  below), and use  `ls`  command to confirm that folders  `RQ1`,  `RQ2`  and  `RQ3`  are in the directory:

```
cd /home/d/Defects4REST-Artifact
source .venv/bin/activate
ls
```

![Terminal LS Screenshot](\Defects4REST-ReplicationPackage\images\Terminal.png)

### RQ1: Common REST API Defect Types
To address RQ1, we first mined a comprehensive and diverse set of real-world REST API–based project repositories from GitHub using specific criteria, including the APIs used in prior REST API research. For the selected APIs, we then mined and created a dataset of closed issue reports associated with modified files and commit messages. Next, we used an LLM-based classifier and manual inspection to filter out issue reports that were not related to REST APIs and constructed a dataset of 607 REST API defects. We used a semi-automated approach that combined clustering and topic modeling with manual validation to derive a novel taxonomy of 6 defect types and 13 sub-types.

To replicate RQ1, switch to `/home/d/Defects4REST-Artifact/RQ1` directory and use  `ls`  to confirm that folders `issue_mining`, `issue_ classification`, and `clustering_topic_modelling` are in the directory:

```
cd /home/d/Defects4REST-Artifact/RQ1

ls
```
![RQ1 Screenshot](\Defects4REST-ReplicationPackage\images\RQ1_screen.png)

### Step 1. RQ1/issue_mining (A valid github token is needed to execute)

**Note:** We have provided our GitHub token for ease of review, so **Step 1.1** is not needed. This will be removed after the artifact is published.

**Step 1.1.** Generate a valid Github Token (Step to generate can be found [here](https://github.com/ANSWER-OSU/defects4rest-evaluation/blob/main/artifact_documentation/GitHubToken.md). )

**Step 1.2.** To mine closed issues from  51 repositories, we provide the script `launch_minebugs.sh` that lists the URL from 51 repositories. For illustration, we will execute the script for restCountries API. Please run the following commands in your terminal: 

```
cd /home/d/Defects4REST-Artifact/RQ1/issue_mining

bash launch_minebugs.sh
```

This step takes approximately 2 minutes to execute for the restCountries repository. Execution time for other repositories may vary depending on the number of issues and commits in the repository being processed. During the execution some issues may be skipped, this occurs when an issue does not have any associated commits.

![issue_mine Screenshot](\Defects4REST-ReplicationPackage\images\mined_restcountries.png)

Once the script finishes executing, the generated issue XML files can be found in the following directory: `/home/d/Defects4REST-Artifact/RQ1/issue_mining/result_mined_issues/issues_xml/restcountries` 

![Restcountries issue_mine Screenshot](\Defects4REST-ReplicationPackage\images\restcountries.png)

To mined issues for one or more of the remaining 50 repositories,uncomment the repository URLs in  `/home/d/Defects4REST-Artifact/RQ1/issue_mining/launch_minebugs.sh` script, rerun the same command `bash launch_minebugs.sh`. 

![Restcountries issue_mine Screenshot](\Defects4REST-ReplicationPackage\images\mined_apis.png)


This will take a approximately 2 hours, so for all the 51 repositories issue mined in this paper, we attached the precomputed result in `/home/d/Defects4REST-Artifact/RQ1/issue_mining//result_mined_issues/issues_xml`

![51 issue_mine Screenshot](\Defects4REST-ReplicationPackage\images\51_mined_issues.png)

#### Step 2. RQ1/issue_classification: A valid OPEN-API Key is needed to execute
Note: This step requires OpenAI key and takes longer to execute because it uses gpt4.1-mini to classify 11,313 issues into REST API and Non REST API defects. Therefore, we provide pre-computed results for all 51 repositories in `/home/d/Defects4REST-Artifact/RQ1/issue_classification/result_classified_issues/`. The results folder contains 51 directories corresponding to each repository, where each directory contains two files: 

(1) `all_issues_with_predictions.csv` that lists all issues with llm prediction, and 

(2) `rest_api_issues.csv` that contains the issues classified as REST API with confidence score more than 0.7. 

![51 Classify Output Screenshot](\Defects4REST-ReplicationPackage\images\51_classified.png)

While not need, the following are the steps to execute the issue classification step.

**Step 2.1.** Navigate to [OpenAI website](https://platform.openai.com/) and generate a valid OpenAPI Key (Steps to generate can be found [here](https://github.com/ANSWER-OSU/defects4rest-evaluation/blob/main/artifact_documentation/OpenAPIToken.md))

**Step 2.2.** Navigate to the working folder `cd /home/d/Defects4REST-Artifact/RQ1/issue_classification`

**Step 2.3.** Open the `classify_issues.py` file and hardcode your generated OpenAPI Key. Replace the YOUR_API_KEY with your generated key from **Step 2.1**

![API_Key Screenshot](\Defects4REST-ReplicationPackage\images\OpenAPI.png)

**Step 2.4.** Save the edited `classify_issues.py` file

**Step 2.5.** To execute `classify_issues.py` for restCountries, navigate to the working directory and run the following command providing the path to your mined issues generated in **Step 1.2** .

```
cd /home/d/Defects4REST-Artifact/RQ1/issue_classification

python classify_issues.py /home/d/Defects4REST-Artifact/RQ1/issue_mining/result_mined_issues/issues_xml/restcountries
```

This process takes approximately 2 minutes to finish for the restCountries repository. Execution time for other repositories may vary depending on the number of issues analyzed. While running `classify_issues.py` on a repository’s XML-based issues, the script iterates over all the issues, prints the LLM prompt, and displays the issue URL, predicted label (bug or no-bug) along with its confidence score for each issue.


![Classify Restcountries issue Screenshot](\Defects4REST-ReplicationPackage\images\restcountries_predict.png)

Once the script finishes executing, it shows the total number of issues analyzed and saves them in `all_issues_with_predictions.csv`, with high-confidence REST API defects saved in `rest_api_issues.csv` 

![Classify Restcountries issue2 Screenshot](\Defects4REST-ReplicationPackage\images\restcountries_predict_number.png)

For example, after the script finishes running on restCountries, these files storing the clasification results for restCountries can be found in the `/home/d/Defects4REST-Artifact/RQ1/issue_classification` folder.

![Classify Output Screenshot](\Defects4REST-ReplicationPackage\images\restcountries_csv.png)


**Step 2.6.** To generate the prediction histogram, run the following command in the terminal:

```
 cd /home/d/Defects4REST-Artifact/RQ1/issue_classification

 python plot_hist.py
 ```
![Histogram Screenshot](\Defects4REST-ReplicationPackage\images\histogram.png)

The script generates a `histogram_confidence.pdf` file  which can be found in the `/home/d/Defects4REST-Artifact/RQ1/issue_classification` folder 

The histogram below shows the 908 issues classified by the LLM as REST API defects, replicating Figure 4 from the paper

![Histogram Screenshot](\Defects4REST-ReplicationPackage\images\Fig_4.png)

#### Step 3: RQ1/clustering_topic_modelling
After the LLM-based classification of 11,313 closed GitHub issues from 51 open-source projects, 908 issues were identified as potential REST API defects. Two authors then independently reviewed these issues using eight predefined criteria to determine whether an issue constitutes a REST API defect. This process resulted in 607 confirmed REST API defects from 50 open-source projects, which were used to derive a taxonomy of REST API defects. This method consists of three main steps:

**Step 3.1.** Preprocessing the issue reports to prepare for topic modeling

To preprocess all issue reports used in this paper, we provide a script `preprocess.sh` which lists the API names from all 51 repositories. This process will take approximately 1 hour. Therefore, for illustration, we will execute the script for `restCountries`. Please run the following in your terminal:

```
cd /home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling

bash preprocess.sh

```

The script cleans and standardizes the textual content of issue titles and descriptions, generates the preprocessed file for restCountries in a few minutes, and saves it as `preprocessed_rest_api_issues_restcounties.csv` in the `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/PreProcessing` folder

![PreProcess RestCountries](\Defects4REST-ReplicationPackage\images\preprocess_rest_bash.png)


To preprocess issue reports for one or more of the remaining 50 repositories, uncomment the corresponding API name in  `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/preprocess.sh` and rerun the same command: `bash preprocess.sh`. 

![All Preprocessing](\Defects4REST-ReplicationPackage\images\preprocess_comment.png)

This process will take approximately one hour. Therefore, for all 51 repositories analyzed in this paper, we provide the precomputed results in `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/PreProcessing`

![51 PreProcessed Result Screenshot](\Defects4REST-ReplicationPackage\images\preprocess_rest.png)


**Step 3.2.** Clustering and Topic Modelling

The preprocessed issue reports from Step **3.1** were clustered and analyzed using topic modeling with DBSCAN and BERTopic to derive defect types. Replicating this step for all 1,800 preprocessed configurations would take approximately **2 hours**. Therefore, we provide the precomputed `hyperparameter_tuning_dbscan.csv` file, which contains the results of all 1,800 configurations and can be used to generate the top 5 configurations. The results of the top 5 models are also available in the folder `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/Top_five_configurations`

**Note: The steps in 3.2.1 (replicating one of the top 5 configurations) and 3.2.2 (generating all configurations) are optional. Following these steps allows you to replicate any one configuration or generate all configurations if desired**

**Step 3.2.1.** Replicating One of the Top 5 Configurations (Model 180)

To replicate any one of the top 5 configurations, edit the config ID in `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/configs.py` with one of the top 5 IDs: 344, 519, 517, 180, or 583.

![Config id](\Defects4REST-ReplicationPackage\images\config_id.png)

For illustration, we will replicate using Config ID 180. Please run the following command in your terminal:

 ``` 
 cd /home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling
 python replicateTM.py   /home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/PreProcessing   /home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/607_defects.csv

```

![I80 Config](\Defects4REST-ReplicationPackage\images\single_configuration.png)

After execution, the outputs corresponding to Model 180 can be found in `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/single_configuration`
 
![I80 Config result](\Defects4REST-ReplicationPackage\images\single_config_result.png)

**Step 3.2.2** Replicating All Clustering and Topic Modeling Used in This Paper

Run the following to replicate all configurations:

 ```
 cd /home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling

 python topicModeling.py /home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/PreProcessing/ 607_defects.csv

```

  During execution, the script loads the issue texts of the Preprocessed issue report in **Step 3.1**, generates sentence embeddings using Sentence-BERT,clusters the issues using DBSCAN, filters out noise and small clusters, applies BERTopic to the filtered issues, evaluates each configuration using silhouette score and topic coherence (C_v) and iterates over all hyperparameter combinations. Once this script finishes executing it generates a summary CSV file `hyperparameter_tuning_dbscan.csv`. 

  ![Clustering](\Defects4REST-ReplicationPackage\images\all_models.png)

This step takes approximately 2 hours to replicate for all preprocessed issue reports. Therefore we provide the precomputed `hyperparameter_tuning_dbscan.csv` file containing the results of the 1,800 distinct configurations evaluated.

To replicate and identify the top five configurations in **Step 3.2.2**, run the following command:

```
python plot.py hyperparameter_tuning_dbscan_607.csv
```

After executing, it identifies the **top five configurations (180, 517, 344, 519, 583, 514)** and generates `pareto_front.png`, which shows the trade-off between Topic Coherence and Silhouette Score, as illustrated in Figure 5 of the paper.

![Figure 5](\Defects4REST-ReplicationPackage\images\Figure_5.png)
![Pareto front Screenshot](\Defects4REST-ReplicationPackage\images\pareto_result.png)


The precomputed results for the top five configurations can be found in the folder `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/Top_five_configurations`

![Top 5 Config](\Defects4REST-ReplicationPackage\images\top5_config.png)


**Step 3.3.** Manual topic analysis and taxonomy construction

The topics produced by the selected top five configurations were manually analyzed by the authors to derive the final taxonomy of REST API defect types. The spreadsheet used for this analysis is available at `/home/d/Defects4REST-Artifact/RQ1/clustering_topic_modelling/result/manual_analysis/Defects4REST.xlsx`, under the tab `ClusterTopic Analysis(6defect)`. The left side of the sheet lists the top five configurations with at least 10 topics, while the right side shows the final manually selected topics, as reported in Table 4 of the paper.

![Table4](\Defects4REST-ReplicationPackage\images\Table_4.png)


### RQ2: File Types and Resolution Time
To answer RQ2, we analyzed the frequency of the manually selected patched files, focusing on both their patch types `(patch_type_analysis)` and the time to fix in days `(time_fix_analysis)`

#### RQ2/patch_type_analysis

To execute `patch_type_analysis` run the following command: 

```
cd /home/d/Defects4REST-Artifact/RQ2/patch_type_analysis

python analyze_patchedfiletypes.py 
```

![Classify Issue Screenshot](\Defects4REST-ReplicationPackage\images\classify_issue.png)

After executing the script, it shows the calculation of the distribution of all REST API patched file types per sub defect type which are *source-files, test-files, configuration-files, documentation-files, data-files, database-files, container-files, and other-files.*  The script also generates a histogram named `patched_file_types_stacked_bar.png` located in the folder: `/home/d/Defects4REST-Artifact/RQ2/patch_type_analysis`. This histogram illustrates the distribution of patched file types and replicates Figure 6 from the paper.

![Classify Issue Histogram](\Defects4REST-ReplicationPackage\images\Figure_6.png)


To replicate the result presented in **Table 5** of the paper:

```
cd /home/d/Defects4REST-Artifact/RQ2/patch_type_analysis

python defect_ranking_frequency.py 
```

After executing, this shows the top 5 REST API defects types ranked by frequency of occurence

![Frequency Ranking](\Defects4REST-ReplicationPackage\images\freq_ranking.png)


![Table 5](\Defects4REST-ReplicationPackage\images\Table_5.png)

####  RQ2/time_fix_analysis

To replicate the result presented in **Table 6** of the paper:

```
cd /home/d/Defects4REST-Artifact/RQ2/time_fix_analysis

python analyze_timetofix.py 
```
After executing, it outputs a summary table showing the minimum, maximum, mean, and standard deviation of time-to-fix (in days) for each defect type

![Fix Time Screenshot](\Defects4REST-ReplicationPackage\images\time_fix_analysis.png)


![Fix Time](\Defects4REST-ReplicationPackage\images\Table_6.png)


### RQ3 REST API Testing Tool Evaluation

To answer this research question, we evaluated four state-of-the-art REST API testing tools on a stratified sample of 30 real-world defects from 11 projects, covering all 6 defect types and 13 subtypes in our taxonomy. The automated test generation tools we evaluated are: Schemathesis, RESTler, EvoMaster, and AutoRestTest.

Each tool was executed with 5 random seeds, with 1 hour timeout per seed, for a total of 600 tool executions (30 defects × 4 tools × 5 seeds). **Since this is a time consuming process (worst case 600 hours, if no tool crashes), we provide pre-computed results obtained by these tools and share our analysis to show their strengths and weaknesses as described below.** Since, the logs from all 600 executions are over 50 GB, we provide them separately at: https://doi.org/10.5281/zenodo.17607138.

In the VM, we provide logs for the 3 defects that are detected by the existing tools in `/home/d/Defects4REST-Artifact/RQ3/generated_logs/` folder. 

The detailed manual analysis for replicating all 30 defects and tools' execution results is available at:
- In VM at: `/home/d/Defects4REST-Artifact/RQ3/manual_replication/Defects4REST_Defect_Detection_Analysis_Report.pdf`
- PDF Report: [Defects4REST-ReplicationPackage/RQ3/manua_replication](https://github.com/ANSWER-OSU/Defects4REST-ReplicationPackage/tree/main/RQ3/manual_replication) 

As shown in Table 8 of the paper, tools detect only 10% (3/30) of real-world defects. 

![Table 8](\Defects4REST-ReplicationPackage\images\Table_8.png)

**While not needed, the VM provides the infrastructure to run the four testing tools on the 30 defects. The following describes the details of the three defects (manual replication) and shows how we found that the tool detected these defects using the generated tests or logs.**   

 
#### The Three Successfully Detected Defects

| Sub Defect Type | Defect | Tool(s) That Detected It |
|---------|--------|--------------------------|
| Container and Resource Quota Handling Errors (ST1) | `seaweedfs#913` | **AutoRestTest** |
| Job Execution and Workflow Configuration Defects (ST2) | `flowable-engine#2584` | **Schemathesis**, **RESTler** |
| Runtime and Dependency Error (ST10) | `nocodb#2776` | **EvoMaster** |

Below, we explain what each defect is and how the tools detected them.

#### Defect 1: SeaweedFS #913 (Detected by AutoRestTest)

In this defect, the `GET /vol/grow` endpoint in SeaweedFS fails to allocate all requested volumes and reports inconsistent free volume counts. When you request a high volume count (e.g., 6,400 volumes), the API stops early with "No more free space left." But when you retry, it says "Only 42 volumes left!" If you then request just those 42, the allocation succeeds. This indicates incorrect resource quota tracking.

While testing an API using AutoRestTest, it produces (1) `operation_status_codes.json` file listing all the endpoints tested along with their response status code frequency, and (2)  `successful_parameters.json` file that stores the randomly generated parameters that led to successful HTTP responses for the triggered endpoints. 

Our analysis of these two files generated when attempting to detect this bug shows that the bug was successfully triggered by AutoRestTest. This was based on the observation that the `operation_status_codes.json` (available at `/home/d/Defects4REST-Artifact/RQ3/generated_logs/seaweedfs_#913/AutoRestTest/seawedfs#913_v1`) file showed that the `get_vol_grow` endpoint (created from `/vol/grow`) that resulted in 84,072 HTTP 406 errors and 186 HTTP 200 successes out of 84,258 total requests, and the `successful_parameters.json` file at `/home/d/Defects4REST-Artifact/RQ3/generated_logs/seaweedfs_#913/AutoRestTest/seawedfs#913_v1` showed diverse values for `count`, `collection`, and `replication` parameters. While the user-filed issue and manual replication uses `count=6400`, AutoRestTest explored diverse count values ranging from 1 to 9343. These high count values successfully returned HTTP 200 responses initially (which is why they appear in `successful_parameters.json`), but out of 84,258 total requests, only 186 returned HTTP 200. The following screenshots show these in the generated files. 

![SeaweedFS precomputed logs](\Defects4REST-ReplicationPackage\images\rq3_seaweedfs_precomputed_logs.png)

![SeaweedFS successful parameters](\Defects4REST-ReplicationPackage\images\rq3_seaweedfs_precomputed_successful_parameters.png)


#### Defect 2: Flowable Engine #2584 (Detected by Schemathesis & RESTler)

In this defect, the REST API no longer allows execution of `moveToHistoryJob` action on dead-letter jobs. When you try to move a failed job to history using the `moveToHistoryJob` action, the API incorrectly returns a 400 error saying "Invalid action, only 'move' is supported" even though `moveToHistoryJob` should be a valid action.

Both tools successfully exercised the `POST /management/deadletter-jobs/{jobId}` endpoint and observed the HTTP 400 error with the message "Invalid action, only 'move' is supported."

**Schemathesis Detection Replication:**
For each run, the tool generated a log file that contains all HTTP requests and responses. For example, the log file generated for seed23 while running Schemathesis on this bug is available at `/home/d/Defects4REST-Artifact/RQ3/generated_logs/flowable-engine_#2584/Schemathesis/logs_bpmn_allphases_seed23/schemathesis-bpmn-seed23.log`.

To find out the HTTP request and response associated with the bug-triggering behavior in the log file, run the following command. As shown in the below screenshot, the tool invoked the triggering endpoint using `jobid` of `0`, that led to HTTP 400 response. 

```bash
sed -n '1041,1062p' /home/d/Defects4REST-Artifact/RQ3/generated_logs/flowable-engine_#2584/Schemathesis/logs_bpmn_allphases_seed23/schemathesis-bpmn-seed23.log
```

![Flowable precomputed Schemathesis logs](\Defects4REST-ReplicationPackage\images\rq3_flowable_precomputed_schemathesis_logs.png)



**RESTler Results:**
For each run, the tool generated a file called `logs/network.testing.[auto_genrated_number].txt` that records all network traffic during testing. For example, the log file generated for seed23 while running RESTler on this bug is available at `/home/d/Defects4REST-Artifact/RQ3/generated_logs/flowable-engine_#2584/RESTler/Fuzz_bfs_seed23/Fuzz/RestlerResults/experiment26/logs/network.testing.140737456978744.1.txt`. 

To find out the HTTP request and response associated with the bug-triggering behavior in the log file, run the following command. As shown in the below screenshot, the tool invoked the triggering endpoint using `jobid` of `fuzzstring`, that led to HTTP 400 response.

```bash
sed -n '8930,8935p' /home/d/Defects4REST-Artifact/RQ3/generated_logs/flowable-engine_#2584/RESTler/Fuzz_bfs_seed23/Fuzz/RestlerResults/experiment26/logs/network.testing.140737456978744.1.txt
```

![Flowable precomputed RESTler logs](\Defects4REST-ReplicationPackage\images\rq3_flowable_precomputed_restler_logs.png)

#### Defect 3: NocoDB #2776 (Detected by EvoMaster)

In this defect, when text column is added (via `POST /api/v2/meta/tables/{tableId}/columns`), and then tried to change that column to a different type like "SingleSelect" (via `PATCH /api/v2/meta/columns/{columnId}`), the API fails with a runtime TypeError: "Cannot read properties of null". The first endpoint results in HTTP 200 while the second one results in HTTP 400 response. 

For each run, EvoMaster produces three test files: `EvoMaster_fault_Test.py`, `EvoMaster_successes_Test.py`, and `EvoMaster_others_Test.py`, each of which contains test cases for the individual endpoints along with expected HTTP responses. The generated test files for this defect show that EvoMaster successfully hit and replicated the responses of both the triggering endpoints. 

To identify the test cases for specific endpoints, run the following command:

```bash
cat /home/d/Defects4REST-Artifact/RQ3/generated_logs/nocodb#2776/EvoMaster/em_results_seed21/EvoMaster_others_Test.py
```
As shown in the screenshot below, EvoMaster generated test case triggering  `POST /api/v2/meta/tables/{tableId}/columns` endpoint leading to 200 response in the `EvoMaster_successes_Test.py` file. 

![NocoDB precomputed verification](\Defects4REST-ReplicationPackage\images\image.png)

```bash
cat /home/d/Defects4REST-Artifact/RQ3/generated_logs/nocodb#2776/EvoMaster/em_results_seed21/EvoMaster_others_Test.py
```
As shown in the screenshot below, EvoMaster generated test case triggering  `PATCH /api/v2/meta/columns/{columnId}` endpoint leading to 400 error in the `EvoMaster_others_Test.py` file. 

![NocoDB precomputed verification](\Defects4REST-ReplicationPackage\images\rq3_nocodb_precomputed_verification.png)

To run individual tools on the three defects, please refer to the instructions at: 

### Tool Issues and Bug Reports

During our evaluation, we encountered several issues with the testing tools and reported them to the respective tool maintainers on GitHub:

### Schemathesis
- **Issue #3377**: [Link to issue and comment](https://github.com/schemathesis/schemathesis/issues/3377#issuecomment-3605862481)

### EvoMaster
- **Issue #1400**: [Link to issue and comment](https://github.com/WebFuzzing/EvoMaster/issues/1400#issuecomment-3728392371)

### AutoRestTest
- **Issue #30**: [Link to issue and comment](https://github.com/selab-gatech/AutoRestTest/issues/30#issuecomment-3605877839)
- **Issue #31**: [Link to issue and comment](https://github.com/selab-gatech/AutoRestTest/issues/31#issuecomment-3605957194)
- **Issue #34**: [Link to issue and event](https://github.com/selab-gatech/AutoRestTest/issues/34#event-21371474087)
- **Issue #36**: [Link to issue and comment](https://github.com/selab-gatech/AutoRestTest/issues/36#issuecomment-3629720422)

