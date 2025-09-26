#!/bin/bash

export DATABRICKS_CONFIG_PROFILE=sdlc

databricks clusters create \
  --json @infra/clusters-create.json \
    > $PWD/infra/clusters-create-output.json