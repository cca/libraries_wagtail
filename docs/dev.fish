#!/usr/bin/env fish
alias k 'kubectl --namespace libraries-wagtail'

function gulp -d 'run gulp watch task'
    pkill gulp
    npx gulp &
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
            echo (date "+%H:%M:%S") "waiting for Docker to start..."
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
    if k --field-selector=status.phase=Running get pods -o name | grep wagtail- &>/dev/null
        echo "✅ Skaffold is already running"
    else
        set_color --bold
        echo "Running Skaffold dev, hit Ctrl + Z to send it to the background or Ctrl + C to stop."
        set_color normal
        skaffold dev --trigger=polling --port-forward
    end
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
switch $option
    case start up
        start
    case stop down
        stop
    case gulp
        gulp
    case '*'
        echo -e "usage: ./docs/dev.fish [ start | stop | up | down | gulp ]\n"
        echo -e "\tstart/up - start the local development site"
        echo -e "\tstop/down - stop the local development toolchaim (skaffold, minikube, docker)"
        echo -e "\tgulp - watch for changes to JS/SCSS files & rebuild them"
end
