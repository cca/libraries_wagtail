#!/usr/bin/env bash
checkfor () {
    command -v $1 >/dev/null 2>&1 || {
        echo -e >&2 "\e[31mMissing $1\e[0m"
        return 1
    }
}

checkfor brew || {
    echo "Installing Homebrew..." && \
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && \
    /usr/local/bin/brew shellenv | source
}
checkfor fish || brew install fish
checkfor docker || brew install --cask docker
checkfor minikube || brew install minikube
checkfor skaffold || brew install skaffold
checkfor gcloud || echo "Google Cloud SDK is used to sync media and database files from the cloud. Install it yourself by following the instructions on https://cloud.google.com/sdk/docs/install-sdk"

minikube config set vm-driver docker
minikube config set cpus 4
minikube config set memory 8192
minikube addons enable metrics-server

echo -e "\nObtain a copy of secrets.env from a developer and place it in kubernetes/local\n"

echo "Do you want to load the (s)taging or (p)roduction database into your local minikube cluster now? You need gcloud installed and docker running but this shouldn't require a secrets.env file. Type \"n\" for \"no\". "
read -r -n 1 -p "[n, p, s]? " result
echo

case ${result} in
    "n")
        echo "Skipping database download. You can run ./docs/sync.fish to download the database later."
        ;;
    "p")
        minikube start --kubernetes-version=1.18.20
        skaffold run -p db-only
        ./docs/sync.fish --prod --db
        ;;
    "s")
        minikube start --kubernetes-version=1.18.20
        skaffold run -p db-only
        ./docs/sync.fish --stage --db
        ;;
    *)
        echo "Unrecognized input \"${result}\", skipping database download. You can run ./docs/sync.fish to download the database later."
        ;;
esac

# shut down minikube if we started it above
if ! minikube status 2&>/dev/null; then
    minikube stop
fi

echo -e "\nDo you want to load the (s)taging or (p)roduction media files onto your local machine? You need gcloud's gsutil installed but docker and minikube do not need to be running. Type \"n\" for \"no\". "
read -r -n 1 -p "[n, p, s]? " result
echo

case ${result} in
    "n")
        echo "Skipping media download. You can run ./docs/sync.fish to download the media files later."
        ;;
    "p")
        ./docs/sync.fish --prod --media
        ;;
    "s")
        ./docs/sync.fish --stage --media
        ;;
    *)
        echo "\nUnrecognized input \"$result\", skipping database download. You can run ./docs/sync.fish to download the media files later."
        ;;
esac
