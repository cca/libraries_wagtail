#!/usr/bin/env fish
echo "Syncing migrations files from minikube pod to host machine..."
if not set -q NS
    set NS libraries-wagtail
end
set POD (kubectl -n$NS get pods -o name | grep wagtail | sed -e 's/pod\///')
for dir in (find . -type d -name migrations)
    kubectl -n$NS cp $POD:(string replace './' '/app/' $dir) $dir
end
