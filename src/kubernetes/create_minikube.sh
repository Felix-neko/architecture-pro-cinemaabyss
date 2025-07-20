
#minikube delete

#minikube start --vm-driver=vmware --cpus=4 --memory=32g --disk-size=40g
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable default-storageclass
minikube addons enable storage-provisioner
minikube addons enable ingress
minikube addons enable ingress-dns
minikube addons enable istio
minikube addons enable istio-provisioner