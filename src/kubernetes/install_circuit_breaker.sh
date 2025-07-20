#!/bin/bash

# Get the directory where this script is located
export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

kubectl apply -f ${SCRIPT_DIR}/circuit-breaker-config.yaml -n cinemaabyss