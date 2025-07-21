#!/bin/bash

# Get the directory where this script is located: {repo_root}/src/kubernetes
export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

kubectl apply -f $SCRIPT_DIR/namespace.yaml

kubectl apply -f $SCRIPT_DIR/configmap.yaml
kubectl apply -f $SCRIPT_DIR/secret.yaml
kubectl apply -f $SCRIPT_DIR/dockerconfigsecret.yaml
kubectl apply -f $SCRIPT_DIR/postgres-init-configmap.yaml
kubectl apply -f $SCRIPT_DIR/postgres.yaml

kubectl apply -f $SCRIPT_DIR/kafka/kafka.yaml
kubectl apply -f $SCRIPT_DIR/monolith.yaml
kubectl apply -f $SCRIPT_DIR/movies-service.yaml

kubectl apply -f $SCRIPT_DIR/events-service.yaml

kubectl apply -f $SCRIPT_DIR/proxy-service.yaml

kubectl apply -f $SCRIPT_DIR/ingress.yaml