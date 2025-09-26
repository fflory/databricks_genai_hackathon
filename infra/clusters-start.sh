#!/usr/bin/env bash

# Set Databricks config profile
export DATABRICKS_CONFIG_PROFILE=sdlc

# export DATABRICKS_CLUSTER_NAME="Felix Flory's Cluster"
export DATABRICKS_CLUSTER_NAME="Felix Flory 16.4 single xl"
export DATABRICKS_CUSTOM_TAGS_PROJECT="databricks_genai_hackathon"

export DATABRICKS_CURRENT_USER="$(databricks current-user me | jq -r '.userName')"
export DATABRICKS_CLUSTER_ID=$(
    databricks clusters list --output json |
    jq -r \
        --arg USER "$DATABRICKS_CURRENT_USER" \
        --arg CLUSTER_NAME "$DATABRICKS_CLUSTER_NAME" \
        --arg PROJECT "$DATABRICKS_CUSTOM_TAGS_PROJECT" \
        '.[] | select(.creator_user_name == $USER and .cluster_name == $CLUSTER_NAME and .custom_tags.project == $PROJECT) | .cluster_id'
)

databricks clusters start "$DATABRICKS_CLUSTER_ID" > $PWD/infra/clusters-start-output.json