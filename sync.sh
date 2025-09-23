#!/usr/bin/env bash

# sync local directory to Databricks workspace directory
# both directories can be git repos

export DATABRICKS_CONFIG_PROFILE=sdlc

export DATABRICKS_USERNAME="$(
    databricks current-user me -o json | jq -r '.userName'
)"

export LOCALDIR=$PWD
export LOCALDIR_LAST=$(basename "$LOCALDIR")
export REMOTE_ROOT="/Users/$DATABRICKS_USERNAME/repos"
export REMOTEDIR="$REMOTE_ROOT/$LOCALDIR_LAST"

echo "local dir: $LOCALDIR"
echo "remote dir: $REMOTEDIR"

databricks workspace mkdirs "$REMOTE_ROOT"
databricks workspace mkdirs "$REMOTEDIR"

databricks sync $LOCALDIR $REMOTEDIR
