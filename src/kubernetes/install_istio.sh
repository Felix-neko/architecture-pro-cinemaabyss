#!/bin/bash

# Get the directory where this script is located
export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

helm install istio-base istio/base -n istio-system --set defaultRevision=default --create-namespace
helm install istio-ingressgateway istio/gateway -n istio-system
helm install istiod istio/istiod -n istio-system --wait
kubectl label namespace cinemaabyss istio-injection=enabled --overwrite
kubectl get namespace -L istio-injection

kubectl apply -f ${SCRIPT_DIR}/circuit-breaker-config.yaml -n cinemaabyss