#!/usr/bin/env bash
DIR="$(dirname "$0")"

checkfor () {
    command -v "$1" >/dev/null 2>&1 || {
        echo -e >&2 "\e[31mMissing $1\e[0m"
        return 1
    }
}

checkfor brew || {
    echo "Installing Homebrew..." && \
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && \
    /usr/local/bin/brew shellenv | source
}
brew bundle install --file "$DIR/Brewfile"
checkfor gcloud || echo "Google Cloud SDK is used to sync media and database files from the cloud. Install it yourself by following the instructions on https://cloud.google.com/sdk/docs/install-sdk"

# Provide minikube with expanded resources
minikube config set cpus 4
# Make this match the version we're using GKE; see `kubectl version`
minikube config set kubernetes-version 1.30.5
minikube config set memory 8192
minikube config set vm-driver docker
# minikube addons enable metrics-server

[ -e "$DIR/../kubernetes/local/secrets.env" ] || echo -e "\nObtain a copy of secrets.env from a developer and place it in kubernetes/local\n"

[ -e "$DIR/../kubernetes/assets/cdi_cca.key" ] || echo -e "\nObtain a copy of the Summon SFTP private key from a developer (it is in Dashlane as \"Summon MFT\") and save it as kubernetes/assets/cdi_cca.key\n"

docker desktop start

echo -e "Do you want to load the (s)taging or (p)roduction database into your local minikube cluster now? You need gcloud installed and docker running but this shouldn't require a secrets.env file. Type \"n\" for \"no\". "
read -r -n 1 -p "[n, p, s]? " result
echo


case ${result} in
    "n")
        echo "Skipping database download. You can run ./docs/sync.fish to download the database later."
        ;;
    "p")
        minikube start
        skaffold run -p db-only
        ./docs/sync.fish --prod --db
        ;;
    "s")
        minikube start
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
        echo -e "\nUnrecognized input \"$result\", skipping database download. You can run ./docs/sync.fish to download the media files later."
        ;;
esac
