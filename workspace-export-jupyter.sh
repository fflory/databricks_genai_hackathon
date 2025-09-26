#!/usr/bin/env bash

# Export a Databricks workspace file to local directory

export DATABRICKS_CONFIG_PROFILE=sdlc

# export WORKSPACEPATH="/Workspace/Users/felix.flory@rgare.com/.bundle/databricks_genai_hackathon/dev/files/notebooks/06-langgraph-multiagent-genie-pat-vs"
export WORKSPACEPATH="/Workspace/Users/felix.flory@rgare.com/.bundle/databricks_genai_hackathon/dev/files/notebooks/manage_deployments"

export FILENAME=$(basename "$WORKSPACEPATH")
# /Users/s0054120/code-byo/databricks_genai_hackathon/notebooks/05_RAG_Genie_agent.ipynb
export LOCALFILE="$PWD/notebooks/$FILENAME.ipynb"

# cd to the local directory where the file should be saved
databricks workspace export "$WORKSPACEPATH" \
  --file "$LOCALFILE" \
  --format "JUPYTER"