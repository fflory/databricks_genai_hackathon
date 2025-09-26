#!/usr/bin/env bash

# Set Databricks configuration profile
export DATABRICKS_CONFIG_PROFILE=sdlc

# Define the path to the cluster output JSON file
export DATABRICKS_CLUSTER_OUTPUT_JSON="infra/clusters-create-output.json"

# Extract cluster ID from the JSON file
export DATABRICKS_CLUSTER_ID=$(
  jq -r '.cluster_id' "$DATABRICKS_CLUSTER_OUTPUT_JSON")

# Start the cluster (commented out for safety)
# databricks clusters start "$DATABRICKS_CLUSTER_ID"

# Display the cluster ID and source file
echo "Started cluster with ID: $DATABRICKS_CLUSTER_ID"
echo "from JSON file $DATABRICKS_CLUSTER_OUTPUT_JSON"