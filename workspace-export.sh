#!/usr/bin/env bash

# Export Databricks workspace files to local directory

export DATABRICKS_CONFIG_PROFILE=sdlc

export DATABRICKS_USERNAME="$(
    databricks current-user me -o json | jq -r '.userName'
)"

# local project root
export LOCALDIR=$PWD
export LOCALDIR_LAST=$(basename "$LOCALDIR")
export REMOTEDIR="/Users/$DATABRICKS_USERNAME/repos/$LOCALDIR_LAST"

echo "local dir: $LOCALDIR"
echo "remote dir: $REMOTEDIR"

# do not include the file extension, it will be added by the databricks cli
export RELATIVEPATH=databricks-client/test

# make sure the local directory exists
# mkdir -p "$(dirname "$LOCALDIR/databricks-client")"

# # jupyter format
# databricks workspace export \
#         $REMOTEDIR/$RELATIVEPATH \
#   --file $LOCALDIR/$RELATIVEPATH.ipynb \
#   --format "JUPYTER"

# python source format
databricks workspace export \
        $REMOTEDIR/$RELATIVEPATH \
  --file $LOCALDIR/$RELATIVEPATH.py \
  --format "SOURCE"

echo "Exported $REMOTEDIR/$RELATIVEPATH"
echo "      to $LOCALDIR/$RELATIVEPATH"

# --format AUTO: DBC for directories and SOURCE for files 
# SOURCE is better than JUPYTER for version control .py files
# but JUPYTER seems to be the default for notebooks in databricks now

databricks workspace export "/Workspace/Users/felix.flory@rgare.com/docs/unstructured-data-pipeline" \
  --file "$PWD/unstructured-data-pipeline.ipynb" \
  --format "JUPYTER"