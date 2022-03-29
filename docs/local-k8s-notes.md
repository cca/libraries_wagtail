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
> minikube config set cpus 4
> minikube config set memory 8192
```

A laptop devoting this many resources to running a local kubernetes cluster will be quite slow; close any unnecessary applications you're running.

To get going:

1. Open Docker Desktop & wait for it to start the docker daemon
2. Run `minikube start` & wait for it to complete
  a. _if you don't have the site's database yet_ run `skaffold -p db-only` and `./docs/sync.fish`
3. Run `skaffold dev` to build the cluster's servers & reload when you change files, see `skaffold help` for other options such as "build", "debug", and "run"
4. Run `kubectl -n libraries-wagtail port-forward service/libraries 8000:8000` to forward the cluster's port 8000 to your host port 8000, now you can access the site at http://localhost:8000
  a. Alternatively, use the Kube Forwarder.app (you can install it with `brew install --cask kube-forwarder)

## Questions & Todos

- [ ] mount the media files at /app/libraries/media
- [ ] smoother solution to port-forwarding (ingress resource with the minikube addon? load balancer?)
- [ ] do we want to mimic Portal's mounted volume approach to the app code?

## Googe Cloud Media & DB Synchronization

You can use `gsutil rsync` to copy media from one storage bucket to another. For very large transfers, try the [Google Cloud Transfer Service](https://console.cloud.google.com/transfer/cloud/jobs). We already have a job configured to copy media from production to staging and it can be run on demand.

To run `google sql export sql` ([docs](https://cloud.google.com/sdk/gcloud/reference/sql/export/sql)) which exports a database to a SQL file in a GS bucket, you need to copy the **service account** name from the SQL instance in Google Console and add it as a principle/permissions to the GS Bucket with at least "Object Creator" privileges.

## March 8, 2022 Dev Ops Meeting

Josh's demo:

<https://gitlab.com/california-college-of-the-arts/cca-k8s-demo/>

Have to redo the port forwarding every time the image is rebuilt with `kubectl port-forward --namespace $NS service/$SERVICE 8000:80`. A k8s ingress resource might be a permanent solution.

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

to get the static files, `gsutil rsync` ([docs](https://cloud.google.com/storage/docs/gsutil/commands/rsync)) from the storage bucket to local dir: <https://gitlab.com/california-college-of-the-arts/portal/-/blob/main/scripts/portaldev-copy-media>
