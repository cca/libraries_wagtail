#!/usr/bin/env fish
echo "Syncing migrations files from minikube pod to host machine..."
set NS libraries-wagtail
set POD (kubectl -n$NS get pods -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep wagtail | head -n1)
for dir in (find . -type d -name migrations)
    set dest $POD:(string replace './' /app/ $dir)
    kubectl -n$NS cp $dest $dir
end
