helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
helm install istio-base istio/base -n istio-system --set defaultRevision=default --create-namespace
helm install istio-ingressgateway istio/gateway -n istio-system
helm install istiod istio/istiod -n istio-system --wait

kubectl create namespace cinemaabyss
kubectl label namespace cinemaabyss istio-injection=enabled --overwrite

helm install cinemaabyss ./helm --namespace cinemaabyss --create-namespace

kubectl get namespace -L istio-injection
kubectl apply -f ./circuit-breaker-config.yaml -n cinemaabyss

kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.25/samples/httpbin/sample-client/fortio-deploy.yaml -n cinemaabyss