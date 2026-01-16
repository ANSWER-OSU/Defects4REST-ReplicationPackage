#-------------------------------------------------------------------------------
# Copyright (c) 2026 Rahil Piyush Mehta, Manish Motwani, Pushpak Katkhede, Kausar Y. Moshood, and Huwaida Rahman Yafie. 
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

import subprocess
import argparse
import os
import json
import shutil

# ============================
# Global default configuration
# ============================

DEFAULT_SEEDS = [21, 23, 33, 42, 2]

# EvoMaster default settings
DEFAULT_EVOMASTER_HOURS = 1          # default 1 hour per seed
EVOMASTER_RATE_PER_MIN = 60

# Schemathesis default settings
SCHEMA_MAX_EXAMPLES = 1
SCHEMA_WORKERS = 4
SCHEMA_RATE_LIMIT = "60/s"

# RESTler default settings (in HOURS)
RESTLER_TIME_BUDGET_DEFAULT = 1      # default 1 hour per seed

# AutoRestTest default settings
AUTOREST_DEFAULT_RUNS = 1
AUTOREST_DEFAULT_SOURCE_DIR = "data/restcountries2"
AUTOREST_DEFAULT_OUTPUT_DIR = "autorest"


def parse_headers(header_args):
    """
    Parse --header "Name: value" arguments into list of (name, value).
    """
    headers = []
    for h in header_args:
        if ":" not in h:
            raise ValueError(f"Invalid header format (expected 'Name: value'): {h}")
        name, value = h.split(":", 1)
        headers.append((name.strip(), value.strip()))
    return headers


# ============================
# EvoMaster
# ============================

def run_evomaster(schema_path, base_url, api_headers, seeds, evomaster_max_time):
    print("\n==============================")
    print(" Running EvoMaster")
    print("==============================\n")

    # Root folder for EvoMaster outputs
    evomaster_root = os.path.join(os.getcwd(), "evomaster")
    os.makedirs(evomaster_root, exist_ok=True)

    # EvoMaster sees schema under /work in the container
    schema_basename = os.path.basename(schema_path)
    evomaster_schema_url = f"file:///work/{schema_basename}"

    for seed in seeds:
        print(f">>> EvoMaster seed {seed}")
        #checkout(args.project, args.bug, seed, "EvoMaster")
        output_folder_host = os.path.join(evomaster_root, f"em_seed_{seed}")
        os.makedirs(output_folder_host, exist_ok=True)
        output_folder_container = f"/work/evomaster/em_seed_{seed}"
        #checkout(project=project, bug=bug, seed=seed, tool="EvoMaster")

        #checkout(seed=seed, tool="EvoMaster")

        cmd = [
            "docker", "run", "--rm", "--network", "host",
            "-v", f"{os.getcwd()}:/work",
            "webfuzzing/evomaster",
            "--blackBox", "true",
            "--problemType", "REST",
            "--bbSwaggerUrl", evomaster_schema_url,
            "--bbTargetUrl", base_url,
            "--maxTime", evomaster_max_time,
            "--ratePerMinute", str(EVOMASTER_RATE_PER_MIN),
            "--seed", str(seed),
            "--outputFolder", output_folder_container,
            "--outputFormat", "PYTHON_UNITTEST",
        ]

        # Map headers to --header0, --header1, ...
        for i, (name, value) in enumerate(api_headers):
            cmd.extend([f"--header{i}", f"{name}: {value}"])

        log_file = os.path.join(evomaster_root, f"em_seed_{seed}.log")
        with open(log_file, "w") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)

        print(f"    Log: {log_file}")
        print(f"    Output: {output_folder_host}\n")


# ============================
# Schemathesis
# ============================

def run_schemathesis(schema_path, base_url, api_headers, seeds):
    print("\n==============================")
    print(" Running Schemathesis")
    print("==============================\n")

    schema_root = os.path.join(os.getcwd(), "schemathesis")
    os.makedirs(schema_root, exist_ok=True)

    for seed in seeds:
        print(f">>> Schemathesis seed {seed}")
        #checkout(args.project, args.bug, seed, "schemathesis")
        har_dir = os.path.join(schema_root, f"logs_har_seed{seed}")
        os.makedirs(har_dir, exist_ok=True)

        junit_path = os.path.join(schema_root, f"st_seed{seed}.xml")

        cmd = [
            "schemathesis", "run",
            schema_path,
            "--url", base_url,
            "--checks", "all",
            "--exclude-checks", "status_code_conformance",
            "--max-examples", str(SCHEMA_MAX_EXAMPLES),
            "--workers", str(SCHEMA_WORKERS),
            "--rate-limit", SCHEMA_RATE_LIMIT,
            "--seed", str(seed),
            "--report", "junit",
            "--report-junit-path", junit_path,
            "--report", "har",
            "--report-dir", har_dir,
        ]

        # Add headers
        for name, value in api_headers:
            cmd.extend(["--header", f"{name}: {value}"])

        log_file = os.path.join(schema_root, f"st_run_seed{seed}.log")
        with open(log_file, "w") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)

        print(f"    Log: {log_file}")
        print(f"    HAR: {har_dir}")
        print(f"    JUnit: {junit_path}\n")


# ============================
# RESTler
# ============================

def run_restler(schema_path, api_headers, seeds, test_port, fuzz_port, time_budget_hours):
    print("\n==============================")
    print(" Running RESTler")
    print("==============================\n")

    restler_root = os.path.join(os.getcwd(), "restler")
    os.makedirs(restler_root, exist_ok=True)

    # Copy schema into restler directory
    schema_filename = os.path.basename(schema_path)
    schema_copy_path = os.path.join(restler_root, schema_filename)
    shutil.copy2(schema_path, schema_copy_path)
    print(f"[Config] Copied schema to: {schema_copy_path}")

    # Build RESTler custom header dict from all headers
    restler_header_dict = {name: [value] for (name, value) in api_headers}

    custom_dict = {}
    if restler_header_dict:
        custom_dict["restler_custom_payload_header"] = restler_header_dict

    custom_dict_path = os.path.join(restler_root, "restler_custom_dict.json")
    with open(custom_dict_path, "w") as f:
        json.dump(custom_dict, f, indent=2)

    # compiler_config.json
    compiler_config = {
        "SwaggerSpecFilePath": [f"/work/restler/{schema_filename}"],
        "CustomDictionaryFilePath": "/work/restler/restler_custom_dict.json"
    }
    compiler_config_path = os.path.join(restler_root, "compiler_config.json")
    with open(compiler_config_path, "w") as f:
        json.dump(compiler_config, f, indent=2)

    restler_out = os.path.join(restler_root, "restler_out")
    os.makedirs(restler_out, exist_ok=True)
    restler_out_container = "/work/restler/restler_out"

    # RESTler compile
    print(">>> RESTler compile")
    compile_cmd = [
        "docker", "run", "--platform", "linux/amd64", "--rm", "--network", "host",
        "-v", f"{os.getcwd()}:/work",
        "mcr.microsoft.com/restlerfuzzer/restler:v8.5.0",
        "dotnet", "/RESTler/restler/Restler.dll",
        "compile", "/work/restler/compiler_config.json",
        "--workingDirPath", restler_out_container,
    ]
    subprocess.run(compile_cmd, check=True)
    print("    Compile done\n")

    # RESTler test
    print(">>> RESTler test")
    test_cmd = [
        "docker", "run", "--platform", "linux/amd64", "--rm", "--network", "host",
        "-v", f"{os.getcwd()}:/work",
        "mcr.microsoft.com/restlerfuzzer/restler:v8.5.0",
        "dotnet", "/RESTler/restler/Restler.dll",
        "--workingDirPath", restler_out_container,
        "test",
        "--grammar_file", f"{restler_out_container}/Compile/grammar.py",
        "--dictionary_file", f"{restler_out_container}/Compile/dict.json",
        "--no_ssl",
        "--target_ip", "host.docker.internal",
        "--target_port", str(test_port),
    ]
    subprocess.run(test_cmd, check=True)
    print("    Test done\n")

    # RESTler fuzz per seed
    for s in seeds:
        print(f">>> RESTler fuzz seed {s}")
        #checkout(args.project, args.bug, s, "RESTler")
        seed_dir = os.path.join(restler_out, f"fuzz_seed_{s}")
        os.makedirs(seed_dir, exist_ok=True)
        seed_dir_container = f"{restler_out_container}/fuzz_seed_{s}"

        fuzz_cmd = [
            "docker", "run", "--platform", "linux/amd64", "--rm", "--network", "host",
            "-v", f"{os.getcwd()}:/work",
            "mcr.microsoft.com/restlerfuzzer/restler:v8.5.0",
            "dotnet", "/RESTler/restler/Restler.dll",
            "--workingDirPath", seed_dir_container,
            "fuzz",
            "--grammar_file", f"{restler_out_container}/Compile/grammar.py",
            "--dictionary_file", f"{restler_out_container}/Compile/dict.json",
            "--no_ssl",
            "--target_ip", "host.docker.internal",
            "--target_port", str(fuzz_port),
            "--time_budget", str(time_budget_hours),
        ]

        subprocess.run(fuzz_cmd, check=True)
        print(f"    Finished seed {s}, output: {seed_dir}\n")


# ============================
# AutoRestTest
# ============================

def run_autorest(autorest_runs, autorest_source_dir, autorest_output_dir):
    print("\n==============================")
    print(" Running AutoRestTest")
    print("==============================\n")

    os.makedirs(autorest_output_dir, exist_ok=True)

    for i in range(1, autorest_runs + 1):
        print(f">>> AutoRestTest run {i}")
        checkout(args.project, args.bug, i, "AutoRestTest")
        # Assumes environment where `poetry run autoresttest` works
        subprocess.run(["poetry", "run", "autoresttest"], check=True)

        dest = os.path.join(autorest_output_dir, f"run{i}")

        if os.path.exists(autorest_source_dir):
            shutil.move(autorest_source_dir, dest)
            print(f"    Moved output to: {dest}")
        else:
            print(f"    ERROR: Expected folder not found: {autorest_source_dir}")
            break

    print("\n    AutoRestTest finished.\n")



# ============================
# Defects4rest
# ============================
def checkout(project, bug, seed, tool):
    print("\n==============================")
    print(f" checkout(): project={project}, bug={bug}, tool={tool}, seed={seed}")
    print("==============================\n")

    # --- Defects4REST checkout command ---
    cmd = [
        "defects4rest",
        "checkout",
        "-p", project,
        "-b", str(bug),
        f"{args.version}",
        "--start"
    ]

    print("Running checkout command:")
    print(" ", " ".join(cmd))

    # Execute
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Checkout failed: {e}")


# ============================
# Main
# ============================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run EvoMaster, Schemathesis, RESTler, and/or AutoRestTest on any project"
    )

    # What to run
    parser.add_argument(
        "--run",
        choices=["evomaster", "schemathesis", "restler", "autorest", "all"],
        default="all",
        help="Which tools to run (default: all)",
    )

    # Seeds
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        help=f"List of seeds to use (default: {DEFAULT_SEEDS})",
    )

    # Shared
    parser.add_argument(
        "--url",
        dest="base_url",
        help="Base API URL (e.g., http://localhost:8030/api/index.php)",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        help='HTTP header, e.g. --header "DOLAPIKEY: 123" (can repeat)',
    )

    # Single schema for EvoMaster / Schemathesis / RESTler
    parser.add_argument(
        "--schema",
        required=True,
        help="Local OpenAPI/Swagger file used by EvoMaster, Schemathesis, and RESTler",
    )

    # EvoMaster
    parser.add_argument(
        "--evomaster-hours",
        type=float,
        help=f"EvoMaster maxTime in HOURS (default: {DEFAULT_EVOMASTER_HOURS})",
    )

    # RESTler
    parser.add_argument(
        "--restler-test-port",
        type=int,
        default=8030,
        help="RESTler test port (default: 8030)",
    )
    parser.add_argument(
        "--restler-fuzz-port",
        type=int,
        default=809,
        help="RESTler fuzz port (default: 809)",
    )
    parser.add_argument(
        "--restler-hours",
        type=float,
        help=f"RESTler fuzz time_budget in HOURS (default: {RESTLER_TIME_BUDGET_DEFAULT})",
    )

    # AutoRestTest
    parser.add_argument(
        "--autorest-runs",
        type=int,
        default=AUTOREST_DEFAULT_RUNS,
        help=f"Number of AutoRestTest runs (default: {AUTOREST_DEFAULT_RUNS})",
    )
    parser.add_argument(
        "--autorest-source-dir",
        default=AUTOREST_DEFAULT_SOURCE_DIR,
        help=f"Directory where AutoRestTest writes its output "
             f"(default: {AUTOREST_DEFAULT_SOURCE_DIR})",
    )
    parser.add_argument(
        "--autorest-output-dir",
        default=AUTOREST_DEFAULT_OUTPUT_DIR,
        help=f"Directory where runs will be stored (default: {AUTOREST_DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--project",
        required=True,
        help="Project name (e.g., dolibarr, flowable, podman)"
    )

    parser.add_argument(
        "--bug",
        required=True,
        help="Bug number in defects4rest"
    )
    parser.add_argument(
        "--version",
        choices=["buggy", "patched"],
        required=True,
        help="Version to check out: buggy or patched for the bug"
    )

    args = parser.parse_args()

    # Decide what to run
    run_evo = args.run in ("evomaster", "all")
    run_sch = args.run in ("schemathesis", "all")
    run_res = args.run in ("restler", "all")
    run_auto = args.run in ("autorest", "all")

    # Seeds
    seeds = args.seeds if args.seeds is not None else DEFAULT_SEEDS
    print(f"[Config] Using seeds: {seeds}")

    # Headers
    api_headers = parse_headers(args.header) if args.header else []
    if api_headers:
        print(f"[Config] Using headers: {api_headers}")
    else:
        print("[Config] No headers configured")

    # Basic validation
    if (run_evo or run_sch or run_res) and not args.base_url:
        print("ERROR: --url (base API URL) is required for EvoMaster/Schemathesis/RESTler.")
        raise SystemExit(1)

    if (run_evo or run_sch or run_res) and not os.path.exists(args.schema):
        print(f"ERROR: Schema file not found: {args.schema}")
        raise SystemExit(1)

    # EvoMaster time
    if args.evomaster_hours is not None:
        evomaster_max_time = f"{args.evomaster_hours}h"
    else:
        evomaster_max_time = f"{DEFAULT_EVOMASTER_HOURS}h"
    print(f"[Config] EvoMaster maxTime: {evomaster_max_time}")

    # RESTler time_budget
    if args.restler_hours is not None:
        restler_time_budget = args.restler_hours
    else:
        restler_time_budget = RESTLER_TIME_BUDGET_DEFAULT
    print(f"[Config] RESTler time_budget (hours): {restler_time_budget}")

    print(f"Selected mode: {args.run}")

    if run_evo:
        run_evomaster(
            schema_path=args.schema,
            base_url=args.base_url,
            api_headers=api_headers,
            seeds=seeds,
            evomaster_max_time=evomaster_max_time,
        )

    if run_sch:
        run_schemathesis(
            schema_path=args.schema,
            base_url=args.base_url,
            api_headers=api_headers,
            seeds=seeds,
        )

    if run_res:
        run_restler(
            schema_path=args.schema,
            api_headers=api_headers,
            seeds=seeds,
            test_port=args.restler_test_port,
            fuzz_port=args.restler_fuzz_port,
            time_budget_hours=restler_time_budget,
        )

    if run_auto:
        run_autorest(
            autorest_runs=args.autorest_runs,
            autorest_source_dir=args.autorest_source_dir,
            autorest_output_dir=args.autorest_output_dir,
        )

    print("=== Done ===")
