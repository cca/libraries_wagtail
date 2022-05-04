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
    eval (minikube docker-env)

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

function cleanup -d 'free up disk space by deleting older docker images'
    set_color --bold
    echo "Cleaning up Docker objects more than a day old on the Minikube server"
    set_color red
    echo "NOTE: this command is untested! Use at your own risk, but the worst result is probably that the next time Skaffold runs it will rebuild the app container from scratch with no cache."
    set_color normal
    read -P "Do you want to continue? (Y/n) " response
    if test (string lower "$response") = 'n'
        echo "OK! Not cleaning up."
        return 0
    end
    minikube ssh 'docker system df'
    # @TODO does this interactive command work over `minikube ssh`?
    minikube ssh 'docker system prune --filter until=24h'
    # Below: find all but the most recent libraries-wagtail images & rm them
    # set most_recent_img (minikube ssh "docker images libraries-wagtail --format '{{.ID}}' | head -n1")
    # docker images libraries-wagtail -f before=$most_recent_img --format '{{.ID}}' | uniq | xargs -n1 docker rmi
end

set option $argv[1]
switch $option
    case start up
        start
    case stop down
        stop
    case gulp
        gulp
    case clean cleanup
        cleanup
    case '*'
        echo -e "usage: ./docs/dev.fish [ start | stop | up | down | gulp ]\n"
        echo -e "\tstart/up - start the local development site"
        echo -e "\tstop/down - stop the local development toolchaim (skaffold, minikube, docker)"
        echo -e "\tgulp - watch for changes to JS/SCSS files & rebuild them"
end
