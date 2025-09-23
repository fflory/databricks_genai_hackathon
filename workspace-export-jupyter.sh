#!/usr/bin/env bash

# Export Databricks workspace files to local directory

export DATABRICKS_CONFIG_PROFILE=sdlc

export WORKSPACEPATH="/Workspace/Users/felix.flory@rgare.com/repos/databricks_genai_hackathon/setup_env/workspace_assets"

export FILENAME=$(basename "$WORKSPACEPATH")

# cd to the local directory where the file should be saved
databricks workspace export "$WORKSPACEPATH" \
  --file "$PWD/setup_env/$FILENAME.ipynb" \
  --format "JUPYTER"