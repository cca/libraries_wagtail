# Local kubernetes development - CCA dev ops

## Running libraries.cca.edu locally (notes)

You will need docker, minikube, kubectl, and skaffold. Many of these are available from different places but they're also all on homebrew. The other sensible place to get these tools is as [gcloud](https://cloud.google.com/sdk/docs/install) CLI components, which we need to interact with our cloud-hosted resources (databases, static files, servers) anyways. To use them, make sure that the "bin" subfolder inside the gcloud tools is on your path.

```sh
> brew i kubectl minikube skaffold
> brew i --cask docker # Docker Desktop app
> # OR use gcloud for these two components
> gcloud components install kubectl minikube skaffold
```

Docker Desktop provides nice visualizations of resources (images, volumes) as well as a set of command-line completions for the most popular shells. You may need to give it additional resources under Settings > Resources.

Minikube can also be configured to use more resources than the defaults:

```sh
> minikube config set vm-driver docker
> minikube config set cpus 6
> minikube config set memory 10000
```

A laptop devoting this many resources to running a local kubernetes cluster will be quite slow; close any unnecessary applications you're running.

To get going:

1. Open Docker Desktop & wait for it to start the docker daemon
2. Run `minikube start` & wait for it to spin up
3. Run `skaffold dev` to build the cluster's servers & reload when you change files, see `skaffold help` for other options such as "build", "debug", and "run"

## March 8, 2022

Josh's demo:

<https://gitlab.com/california-college-of-the-arts/cca-k8s-demo/>

Have to redo the port forwarding every time the image is rebuilt with `kubectl port-forward --namespace $NS service/$SERVICE 8000:80`. A k8s ingress resource is might be a permanent solution.

My major questions: how to run a Postgres DB and ES servers connected to app, how to sync data, secrets/env.

<https://gitlab.com/california-college-of-the-arts/portal/-/tree/main/kubernetes/bases/dev-tools>

create deployment of postgres <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/kubernetes/bases/dev-tools/postgres/deployment.yaml> with a persistent volume <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/kubernetes/bases/dev-tools/postgres/volumes.yaml>
create service exposing it at port 5432 <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/kubernetes/bases/dev-tools/postgres/service.yaml>
this gives you a db URL (see Portal) you can config in an env
    choose db secrets in configMap <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/kubernetes/bases/dev-tools/postgres/configMap.yaml>
which is then swapped in the libraries image

persistent volumes are stored _on the minikube server_ in the /data dir, you can `minikube ssh` to go into the server and look around

`minikube dashboard` opens a nice web UI to visualize the k8s resources

kustomize secrets generator can pull values from a gitignored .env file, you combine those with your configMap.yml for all your app's secrets/environment variables

to get a fresh copy of the database, use GCP commands and then drop/create the db on your local k8s cluster: <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/scripts/portaldev-copy-db>

to get the static files, `gsutil cp` from the storage bucket to local dir: <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/scripts/portaldev-copy-media>

## Outstanding Questions

Why the 2 elasticsearch containers?

Why is the Postgres service a NodePort one rather than ClusterIP? Is it needed outside the cluster for some reason?

Next thing to work on: actually using the libraries Wagtail app and its Dockerfile.
