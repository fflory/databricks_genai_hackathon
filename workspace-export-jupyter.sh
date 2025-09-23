#!/usr/bin/env bash

# Export a Databricks workspace file to local directory

export DATABRICKS_CONFIG_PROFILE=sdlc

export WORKSPACEPATH="/Workspace/Users/felix.flory@rgare.com/repos/databricks_genai_hackathon/setup_env/workspace_assets"

export FILENAME=$(basename "$WORKSPACEPATH")
export LOCALFILE="$PWD/setup_env/$FILENAME.ipynb"

# cd to the local directory where the file should be saved
databricks workspace export "$WORKSPACEPATH" \
  --file "$LOCALFILE" \
  --format "JUPYTER"