#!/usr/bin/env bash
checkfor () {
    command -v $1 >/dev/null 2>&1 || {
        echo -e >&2 "\e[31mMissing $1\e[0m"
        return 1
    }
}

checkfor brew || {
    echo "Installing Homebrew..." && \
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
}
checkfor docker || brew install --cask docker
checkfor minikube || brew install minikube
checkfor skaffold || brew install skaffold
checkfor gcloud || echo "Google Cloud SDK is used to sync media and database file from the cloud. Install it yourself by following the instructions on https://cloud.google.com/sdk/docs/install-sdk"

minikube config set vm-driver docker
minikube config set cpus 6
minikube config set memory 10000

echo "Obtain a copy of secrets.env from a developer and place it in kubernetes/local"
