#!/usr/bin/env bash

# Export a Databricks workspace file to local directory

export DATABRICKS_CONFIG_PROFILE=sdlc

export WORKSPACEPATH="/Workspace/Users/felix.flory@rgare.com/.bundle/databricks_genai_hackathon/dev/files/agents/multiagent_genie_vs.py"

export FILENAME=$(basename "$WORKSPACEPATH")
export LOCALFILE="$PWD/agents/$FILENAME"

# cd to the local directory where the file should be saved
databricks workspace export "$WORKSPACEPATH" \
  --file "$LOCALFILE" \
  --format "SOURCE"