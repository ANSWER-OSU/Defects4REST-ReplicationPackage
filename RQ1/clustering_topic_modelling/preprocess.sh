#!/bin/bash
# preprocess_selected_apis.sh
# Script to preprocess selected APIs and save outputs in result/PreProcessing

cd "$(dirname "$0")"

BASE_DIR="../issue_classification/result_classified_issues"
OUTPUT_DIR="./result/PreProcessing"
mkdir -p "$OUTPUT_DIR"

# Comment out any API you don't want to preprocess
# Only restcountries is active
apis=(
     "restcountries"
#    "Annif"
#    "apistar"
#    "awx"
#    "catwatch"
#    "cgm-remote-monitor"
#    "cwa-verification-server"
#    "digdag"
#    "djoser"
#    "dolibarr"
#    "DSpace"
#    "elassandra"
#    "elasticsearch"
#    "enviroCar-server"
#    "flowable-engine"
#    "Ghost"
#    "granary"
#    "harness"
#    "hummingbot"
#    "hydrus"
#    "kafka-rest"
#    "label-studio"
#    "localsend"
#    "management-api-for-apache-cassandra"
#    "mastodon"
#    "Mobile-Security-Framework-MobSF"
#    "modular-monolith-with-ddd"
#    "mygpo"
#    "netbox"
#    "nocodb"
#    "nopCommerce"
#    "OrchardCore"
#    "outline-server"
#    "plane"
#    "podman"
#    "redash"
#    "refugerestrooms"
#    "seaweedfs"
#    "shopizer"
#    "signal-cli-rest-api"
#    "silver"
#    "SpaceX-API"
#    "spring-petclinic-rest"
#    "stf"
#    "strapi"
#    "supabase"
#    "traefik"
#    "uptime-kuma"
#    "vercel"
#    "WP-API"
#    "zuul"
)
S
for api_name in "${apis[@]}"; do
    # skip commented out APIs
    [[ "$api_name" =~ ^#.* ]] && continue

    input_csv="$BASE_DIR/$api_name/rest_api_issues.csv"

    if [ -f "$input_csv" ]; then
        echo "Preprocessing $api_name..."

        # Run preprocessing
        python preprocess_issue.py "$api_name" "$input_csv"

        # Move the generated file to OUTPUT_DIR
        GENERATED_FILE="preprocessed_rest_api_issue_${api_name}.csv"
        if [ -f "$GENERATED_FILE" ]; then
            mv "$GENERATED_FILE" "$OUTPUT_DIR/"
            echo "Saved preprocessed file to $OUTPUT_DIR/$GENERATED_FILE"
        else
            echo "Warning: Expected output file $GENERATED_FILE not found!"
        fi

        echo "----------------------------------"
    else
        echo "No rest_api_issues.csv found for $api_name, skipping..."
    fi
done

echo "Selected preprocessing complete. Files are in $OUTPUT_DIR"

