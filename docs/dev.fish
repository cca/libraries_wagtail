#!/usr/bin/env fish
alias k 'kubectl --namespace libraries-wagtail'

function pf -d 'redo libraries service port-forwarding'
    pkill -f 'port-forward service/libraries'
    k port-forward service/libraries 8000:8000 &
end

function start -d 'start the local wagtail application'
    # start docker
    if docker info &>/dev/null
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
            echo (date "+%H:%m:%S") "waiting for Docker to start..."
            sleep 10
        end
    end

    # start minikube
    if minikube status &>/dev/null
        echo "✅ Minikube is running"
    else
        minikube start # --kubernetes-version=1.18.20
    end

    # run skaffold
    if k --field-selector=status.phase=Running get pods 2>/dev/null | grep wagtail-
        echo "✅ Skaffold is already running"
    else
        skaffold dev &
    end

    # port-forward
    echo "Starting kubernetes port-forwarding. The application will be available at http://localhost:8000"
    echo "If your k8s deployment is recreated, you have to redo the port-forwarding. You can tell this has happened if you see 'Error: No such container' and the website stops loading but the deployments are up (kubectl -n libraries-wagtail get deploy)."
    # @TODO can we watch for deployment changes, then automatically redo port-forwarding when we see them?
    # Might be difficult if not completely impossible
    pf
end

function stop -d 'stop the local development tools'
    echo "Stopping the local development toolchain..."
    echo "Stopping port-forwarding"
    pkill -f 'port-forward service/libraries'
    echo "Stopping skaffold"
    pkill -f 'skaffold dev'
    echo "Stopping minikube"
    # if you try to stop minikube & it's not started it loops infinitely
    if minikube status &>/dev/null
        minikube stop
    end
    echo "Stopping docker"
    pkill dockerd 2>/dev/null
    killall Docker 2>/dev/null
end

set option $argv[1]

if test "$option" = start; or test "$option" = up
    start
else if test "$option" = stop; or test "$option" = down
    stop
else if test "$option" = pf
    pf
else
    echo -e "usage: ./docs/dev.fish [ start | stop | up | down | pf ]\n"
    echo -e "\tstart/up - start the local development site"
    echo -e "\tstop/down - stop the local development toolchaim (skaffold, minikube, docker)"
    echo -e "\tpf - redo port-forwarding (after deployment changes)"
end
