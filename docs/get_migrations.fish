#!/usr/bin/env fish
echo "Syncing migrations files from minikube pod to host machine..."
set NS libraries-wagtail
set POD (kubectl -n$NS get pods -o jsonpath='{.items[0].metadata.name}' | grep wagtail | head -n1)
for dir in (find . -type d -name migrations)
    kubectl -n$NS cp $POD:(string replace './' '/app/' $dir) $dir
end
