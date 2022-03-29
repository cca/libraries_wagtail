#!/usr/bin/env fish
function start -d 'start the local wagtail application'
    # start docker
    if not docker info &>/dev/null
        echo "✅ Docker is running"
    else
        if command --query dockerd
            dockerd &>/dev/null &
        else if [ -d /Applications/Docker.app ]
            open -a /Applications/Docker.app
        else
            echo "Error: dockerd isn't in PATH and /Applications/Docker.app doesn't exist, are you sure you have Docker installed?"
            exit 1
        end

        while not docker info &>/dev/null
            echo (date "+%H:%m") "waiting for Docker to start..."
            sleep 2
        end
    end

    # start minikube
    if not minikube status &>/dev/null
        minikube start
    else
        echo "✅ Minikube is running"
    end

    # run skaffold (in background? or else we can't run kubectl port-forward)
    if not ps aux | grep skaffold
        skaffold run dev &
    else
        echo "✅ Skaffold is already running"
    end

    # port-forward
    echo "Starting kubernetes port-forwarding. The application will be available at http://localhost:8000"
    echo "If your k8s deployment is recreated, you have to redo the port-forwarding. You can tell this has happened if you see 'Error: No such container' and the website stops loading but the deployments are up (kubectl -n libraries-wagtail get deploy)."
    # @TODO can we send kubectl port-forward to a background job, watch for deployment changes,
    # then rerun it if we see one happening? Might be difficult if not completely impossible
    kubectl --namespace libraries-wagtail port-forward service/libraries 8000:8000
end

function stop -d 'stop the local development tools'
    echo "NOTE: stop isn't implemented yet, needs to be tested"
    exit
    killall skaffold
    minikube stop
    killall Docker.app
end

set option $argv[1]

if [ "$option" = 'start' -o "$option" = 'up' ]
    start
else if [ "$option" = 'stop' -o "$option" = 'down' ]
    stop
else
    echo "usage: ./docs/dev.fish [ start | stop | up | down ]"
    echo "start/up starts the local development site"
    echo "stop/down stops all the local development tools (skaffold, minikube, docker) in the right order"
end
