# Check if Minikube is installed
if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Output "Minikube not found. Please install Minikube."
    exit 1
}
# Start Minikube cluster
minikube start --driver=hyperv # Use --driver=docker for Docker Desktop
# Verify cluster status
kubectl cluster-info
# Retrieve available pods
kubectl get pods --all-namespaces