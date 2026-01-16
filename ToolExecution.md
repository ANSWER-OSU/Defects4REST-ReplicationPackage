### Running Testing Tools on Defects4REST Defects

**Important Note on Execution Time:**  
Each tool execution takes 1 hour per seed (as configured in our paper). With 5 seeds, that's 5 hours per tool per defect. For all 3 detected defects × 4 tools × 5 seeds, complete execution would take approximately **60 hours of total runtime**.

#### Requirements

##### System Requirements
- Python 3.10+ (Pre-installed in VM)
- Docker + Docker Compose installed and running (Pre-installed in VM)
- Defects4REST installed (Pre-installed in VM - verify with `defects4rest --help`)
  - Activate from anywhere: `source /home/d/Defects4REST/defects4rest/bin/activate`
  - Located at: `/home/d/Defects4REST`

##### Tool Prerequisites (All Pre-installed in VM)
- Schemathesis: Version 4.3.9 (installed via pip)
- EvoMaster: Runs on Docker (Docker images available)
- RESTler**: Runs on Docker (Docker images available)
- AutoRestTest: Installed at `/home/d/autoresttest` (uses Poetry)

##### What You Need to Provide
- OpenAI API Key: Required for AutoRestTest.
---

#### Example 1: SeaweedFS #913 (AutoRestTest Detection)
This example demonstrates how **AutoRestTest** detects a real defect in SeaweedFS.

**Step 1.** Go to the RQ3/script directory and activate python enviroment.

```bash
cd /home/d/Defects4REST-Artifact/RQ3/script

source /home/d/Defects4REST/defect4rest_env/bin/activate
```

**Step 2.** Deploy the Buggy Version

```bash
defects4rest checkout -p seaweedfs -i 913 --buggy --start
```

![SeaweedFS checkout buggy](/artifact_documentation/images/rq3_seaweedfs_checkout_buggy.png)


**Step 3.** Confirm Containers Are Running

```bash
docker ps
```

You should see the SeaweedFS container running on a specific port (note this port for the next step).

![SeaweedFS docker ps](/artifact_documentation/images/rq3_seaweedfs_docker_ps.png)


**Step 4.** Configure AutoRestTest with OpenAI API Key

Navigate to the AutoRestTest directory:

```bash
cd /home/d/autoresttest
```

##### Activate the Virtual Environment

Before configuring the API key, activate the AutoRestTest virtual environment:

```bash
source autoresttest/bin/activate
```

You should see `(autoresttest)` appear in your terminal prompt, indicating the environment is active.

##### Add API Key to .env File

Create or edit the `.env` file:

```bash
echo "OPENAI_API_KEY=''" >> .env
```


**Step 5.** Verify SeaweedFS Specification File

Ensure the SeaweedFS OpenAPI specification is located at:

```bash
ls /home/d/autoresttest/specs
```

You should see the SeaweedFS specification file `seaweedfs.yaml`.

**Step 6.** Run AutoRestTest

Now run AutoRestTest using Poetry. This will use the specification file in the `specs` directory:

```
poetry run autoresttest
```

![SeaweedFS AutoRestTest run](/artifact_documentation/images/rq3_seaweedfs_autorest_run.png)

After the run completes, AutoRestTest logs will be available at `/home/d/Defects4REST-Artifact/RQ3/script/logs/seaweedfs913/AutoRestTest/`

**Step 7.** Clean Up

Stop and remove containers, volumes, and networks:

```bash
defects4rest checkout -p seaweedfs -i 913 --clean
```

![SeaweedFS stop clean](/artifact_documentation/images/rq3_seaweedfs_stop_clean.png)

---

#### Example 2: Flowable Engine (Schemathesis + RESTler Detection)

This example demonstrates how both Schemathesis and RESTler detect the same defect in Flowable Engine.
**Step 1.** Go to the RQ3/script directory and activate python enviroment.

```bash
cd /home/d/Defects4REST-Artifact/RQ3/script

source /home/d/Defects4REST/defect4rest_env/bin/activate
```

**Step 2.** Deploy the Buggy Version

```bash
defects4rest checkout -p flowable-engine -i 2584 --buggy --start
```

![Flowable checkout buggy](/artifact_documentation/images/rq3_flowable_checkout_buggy.png)

**Step 3.** Confirm Containers Are Running

```bash
docker ps
```

You should see the Flowable Engine container running on port 8080.

![Flowable docker ps](/artifact_documentation/images/rq3_flowable_docker_ps.png)

**Step 4a.** Run Schemathesis

```bash
python3 run_all.py \
  --run schemathesis \
  --project flowable-engine \
  --bug 2584 \
  --version buggy \
  --schema /home/d/Defects4REST-Artifact/RQ3/generated_logs/flowable-engine_#2584/bpmn.json \
  --url http://localhost:8080/flowable-rest/
```


![Flowable Schemathesis](/artifact_documentation/images/rq3_flowable_schemathesis.png)

After the run completes, Schemathesis logs will be available at `/home/d/Defects4REST-Artifact/RQ3/script/logs/flowable-engine_#2584/schemathesis/`

**Step 4b** Run RESTler

```bash
python3 run_all.py \
  --run restler \
  --project flowable-engine \
  --bug 2584 \
  --version buggy \
  --schema /home/d/Defects4REST-Artifact/RQ3/generated_logs/flowable-engine_#2584/bpmn.json \
  --url http://localhost:8080/flowable-rest/ \
  --restler-hours 1
```


![Flowable RESTler](/artifact_documentation/images/rq3_flowable_restler.png)

After the run completes, RESTler logs will be available at `/home/d/Defects4REST-Artifact/RQ3/script/logs/flowable-engine_#2584/restler/`

**Step 5** Clean Up

Stop and remove containers, volumes, and networks:

```bash
defects4rest checkout -p flowable-engine -i 2584 --clean
```

![Flowable stop clean](/artifact_documentation/images/rq3_flowable_stop_clean.png)

---

#### Example 3: NocoDB #2776 (EvoMaster Detection)

This example demonstrates how EvoMaster detects a defect in NocoDB.

**Step 1.** Go to the RQ3/script directory and activate python enviroment.

```bash
cd /home/d/Defects4REST-Artifact/RQ3/script

source /home/d/Defects4REST/defect4rest_env/bin/activate
```

**Step 2.** Deploy the Buggy Version

```bash
defects4rest checkout -p nocodb -i 2776 --buggy --start
```

![NocoDB checkout buggy](/artifact_documentation/images/rq3_nocodb_checkout_buggy.png)

**Step 3.** Confirm Containers Are Running

```bash
docker ps
```

You should see the NocoDB container running on port 8080.

![NocoDB docker ps](/artifact_documentation/images/rq3_nocodb_docker_ps.png)

**Step 4.** Generate API Token (`xc-token`) from NocoDB UI

An authentication header is required to access NocoDB APIs. Follow these steps to generate the required token:

**Step 4a.** Open NocoDB in Your Browser

Navigate to:
- `http://localhost:8080`

![NocoDB landing](/artifact_documentation/images/rq3_nocodb_landing.png)

**Step 4b.** Go to "My Projects"

![NocoDB my projects](/artifact_documentation/images/rq3_nocodb_my_projects.png)

**Step 4c.** Create a New Project

From **My Projects**:
1. Click New Project → Create**
2. Enter a project name (e.g., `admin`)
3. Click Create**

![NocoDB create project](/artifact_documentation/images/rq3_nocodb_create_project.png)

**Step 4d.** Open Team & Settings → API Tokens

Inside the project:
1. Click Team & Settings** (bottom-left corner)
2. Go to Team & Auth**
3. Open API Tokens Management
4. Click Add New Token

![NocoDB team and settings](/artifact_documentation/images/rq3_nocodb_team_and_settings.png)

![NocoDB API tokens management empty](/artifact_documentation/images/rq3_nocodb_api_tokens_empty.png)

**Step 4e.** Copy the Generated Token

After creating the token, click the copy icon to copy it to your clipboard. Save this token for the next step.

![NocoDB API token created](/artifact_documentation/images/rq3_nocodb_api_token_created.png)

**Step 5.** Run EvoMaster (1 Hour per Seed)

**Important:** Replace the `xc-token` value below with the token you generated in Step 3.5.

```bash
python3 run_all.py \
  --run evomaster \
  --project nocodb \
  --bug 2776 \
  --version buggy \
  --schema "/home/d/Defects4REST-Artifact/RQ3/generated_logs/nocodb#2776/nocodb.json" \
  --url "http://localhost:8080" \
  --evomaster-hours 1 \
  --header 'xc-token: YOUR_GENERATED_TOKEN_HERE'
```

**Example (use your actual token):**

```bash
python3 run_all.py \
  --run evomaster \
  --project nocodb \
  --bug 2776 \
  --version buggy \
  --schema "/home/d/Defects4REST-Artifact/RQ3/generated_logs/nocodb#2776/nocodb.json" \
  --url "http://localhost:8080" \
  --evomaster-hours 1 \
  --header 'xc-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YXNkZnM0Nzc2ZXhhbXBsZQ'
```

![NocoDB EvoMaster](/artifact_documentation/images/rq3_nocodb_evomaster.png)

After the run completes, EvoMaster logs will be available at `/home/d/Defects4REST-Artifact/RQ3/script/logs/nocodb#2776/evomaster/`

**Step 6.** Clean Up

Stop and remove containers, volumes, and networks:

```bash
defects4rest checkout -p nocodb -i 2776 --clean
```

![NocoDB stop clean](/artifact_documentation/images/rq3_nocodb_stop_clean.png)
