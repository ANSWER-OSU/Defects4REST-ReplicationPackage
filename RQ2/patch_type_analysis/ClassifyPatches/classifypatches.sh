#!/bin/bash

# List of API names

apis=("Annif" "apistar" "awx" "catwatch" "cgm-remote-monitor" "cwa-verification-server" \
      "digdag" "djoser" "dolibarr" "DSpace" "elassandra" "elasticsearch" "enviroCar-server" \
      "flowable-engine" "Ghost" "granary" "harness" "hummingbot" "hydrus" "kafka-rest" \
      "label-studio" "localsend" "management-api-for-apache-cassandra" "mastodon" \
      "Mobile-Security-Framework-MobSF" "modular-monolith-with-ddd" "mygpo" "netbox" \
      "nocodb" "nopCommerce" "OrchardCore" "outline-server" "plane" "podman" "redash" \
      "refugerestrooms" "restcountries" "seaweedfs" "shopizer" "signal-cli-rest-api" \
      "silver" "SpaceX-API" "spring-petclinic-rest" "stf" "strapi" "supabase" "traefik" \
      "uptime-kuma" "vercel" "WP-API" "zuul")

# Loop through each API and run the commands
for api in "${apis[@]}"
do
    echo "Processing $api..."
    python classifyPatches.py "../../rest-taxonomy-study/data/mined_issues/${api}/" "../../rest-taxonomy-study/results/IssueClassification/${api}/rest_api_issues.csv"
    
    # Move the output CSV file to the PreProcessing directory
    mv "rest_api_issues_with_patchtyes.csv" "rest_api_issues_with_patchtyes_${api}.csv"
done

echo "All APIs processed."
