#!/bin/bash

# Get the directory where this script is located: {repo_root}/src/kubernetes
export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

helm install cinemaabyss ${SCRIPT_DIR}/helm --namespace cinemaabyss --create-namespace