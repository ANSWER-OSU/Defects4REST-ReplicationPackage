## **Overview**
This script automates the execution of four REST API testing tools:

-   **EvoMaster**
-   **Schemathesis**
-   **RESTler**
-   **AutoRestTest**
   

The script is generic and can be used for any REST API project by supplying the OpenAPI/Swagger specification, base API URL, and optional headers.
Each tool’s output is stored in a separate directory (evomaster/, schemathesis/, restler/, autorest/).

This script does not modify any testing tool.
## **Requirements**
-   Python **3.10+**
-   Docker installed and running
-   Defects4REST v1
-   Schemathesis installed: `pip install schemathesis`
-   AutoRestTest installed via Poetry (if you use the AutoRestTest option)  [setup link](https://github.com/selab-gatech/AutoRestTest/)

## **Usage**

###  Run

    python3 run_tools.py \
      --run all \
      --project podman \
      --bug 1 \
      --version buggy \
      --schema api.json \
      --url http://localhost:8080 \
      --header "Authorization: Bearer TOKEN" \
      --autorest-workdir /path/to/AutoRestTest/AutoRestTest \
      --autorest-runs 5

This runs:

-   EvoMaster (all 5 seeds, 1 hour per seed)
-   Schemathesis (all 5 seeds)
-   RESTler test + fuzz (per 5 seed, 1 hour per seed)
-   AutoRestTest N times


### **Other Command Line Arguments**
- EvoMaster runtime (hours) : `--evomaster-hours 2`
- Restler runtime (hours) :  `--restler-hours 3`
- Seed (override default [21, 23, 33, 42, 2]):  `--seeds 21 2 34` 
- Autotest runs:  `--autorest-runs 6`
- The script accepts a `--run` argument to control which tools to execute:
	- `evomaster`
	- `schemathesis`
	- `restler`
	- `autorest`
	- `all` (default)



### **Output Structure**

    evomaster/
      em_seed_21/
      em_seed_23/
      ...
      em_seed_21.log
      ...
    schemathesis/
      logs_har_seed21/
      st_seed21.xml
      st_run_seed21.log
      ...
    restler/
      restler_out/
        Compile/
        test/
        fuzz_seed_21/
      restler_custom_dict.json
      compiler_config.json
    autorest/
      run1/
      run2/
      run3/
      ...