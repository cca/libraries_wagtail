# Libraries Wagtail Site

This folder contains the generic documentation for the CCA Libraries Wagtail site as well as development scripts, all of which are meant to be run from the parent directory. Most of the site's apps also have readme files with more information specific to them.

## Running Wagtail Locally

The ./docs/setup.sh script should get us all the needed dependencies. These are extra details and some manual steps.

We need docker, minikube, kubectl, and skaffold. Many of these are available from different places but they're also all on homebrew. The other sensible place to get these tools is as [gcloud](https://cloud.google.com/sdk/docs/install) CLI components, which we need to interact with our cloud-hosted resources (databases, static files, servers) anyways. To use them, we make sure that the "bin" subfolder inside the gcloud tools is on our path.

```sh
> brew i kubectl minikube skaffold # kubectl is a dependeny of homebrew minikube
> brew i --cask docker # Docker Desktop app
> # OR use gcloud for these two components
> gcloud components install kubectl minikube skaffold
```

Docker Desktop provides visualizations of resources (images, volumes). We need to give it additional resources under Settings > Resources. Generally, give Docker access to all CPUs, almost all RAM, and multiple gigabytes of swap space. It needs _at least_ the amount of memory that minikube uses (see setup.sh).

We currently run the entire app in minikube, including postgres database and elasticsearch, but other CCA teams (like cca.edu) are moving to running only Wagtail locally while using a cloud-hosted database and search engine. Ngoc has a notebook on how this conversion worked if we want to go that route.

To authenticate locally, be sure to use `127.0.0.1` as the server domain, not `locahost`, as SSO is configured to work with the former and not the latter.

### Port-forwarding

If we use dev.fish, Skaffold should mostly take cares of this. Otherwise, there are three ways to forward a port on the minikube cluster so we can open the website using our localhost domain in a browser:

1. (easiest) run `skaffold dev` with the `--port-forward` flag. The [port-forward](https://skaffold.dev/docs/pipeline-stages/port-forwarding/) configuration is in Skaffold.yml. If we omit this from the Skaffold profile but use the `--port-forward` flag, Skaffold will automatically create forwarding for all services, but if the pods are recreated it will not recreate the forwarding, so this is not recommended.
2. Run `kubectl -n libraries-wagtail port-forward service/libraries 8000:8000`, this is what Skaffold does behind the scenes
3. Use [Kube Forwarder.app](https://kube-forwarder.pixelpoint.io/) (install it with `brew install --cask kube-forwarder`) which provides a GUI interface around port forwarding

### Kubernetes Namespace stuck in "terminating" status

To rebuild the local dev application, Skaffold deletes all the kubernetes resources in the app's `libraries-wagtail` namespace. Sometimes, the namespace itself gets stuck in a "terminating" status. [This article](https://www.redhat.com/sysadmin/troubleshooting-terminating-namespaces) explains what's happening: the namespace's "finalizer" never allows it to be removed. The solution is to edit the namespace and remove the finalizer.

```sh
k get ns libraries-wagtail -o json > ns.json
# edit the JSON representation, remove 'kubernetes' from the 'finalizers' array
$EDITOR ns.json
# PUT the edited namespace to Kubernetes
# PORT may change; look at where `minikube dashboard` is running to find it
PORT=60406 curl -k -H "Content-Type: application/json" -X PUT --data-binary @ns.json http://127.0.0.1:$PORT/api/v1/namespaces/libraries-wagtail/finalize
```

(in this code `k` is the libraries `kubectl -n $NS` alias)

### Minikube Disk Usage

Note that persistent volumes are stored _on the minikube server_ in the /data dir, we can `minikube ssh` to go into the server to look around. The server's docker instance also stacks up old versions of our images over time and needs to be pruned. Below is an example of using docker's [filters](https://docs.docker.com/engine/reference/commandline/images/#filter) to remove all but the last couple images:

```fish
# set your local docker environment to reference the minikube docker
> minikube -p minikube docker-env | source
> docker images --filter reference=libraries-wagtail
REPOSITORY        TAG                                                                IMAGE ID       CREATED         SIZE
libraries-wagtail 552e430472ee46b4a5b551dd13e84243a9c6dbcd4a116689bbf06ede8fbd3884   552e430472ee   2 weeks ago     1.24GB
libraries-wagtail ep-full-0.28                                                       552e430472ee   2 weeks ago     1.24GB
libraries-wagtail 8329aa97580d74cebbf9119904262c74e9d1b976198a722e2ab2076f7378e690   8329aa97580d   2 months ago    1.24GB
...
# we want to keep the images from 2 weeks ago & remove older libraries-wagtail images
# first, confirm that this command lists what we want to remove
> docker images --filter reference=libraries-wagtail --filter before=552e430472ee
# now remove them, the -q flag causes the output to be only image IDs
> docker rmi (docker images -q --filter reference=libraries-wagtail --filter before=552e430472ee)
# we may need the -f/--force flag to rmi if docker warns us that some images are
# "referenced in multiple repositories". To do everything all in one command (BE CAREFUL):
> docker rmi -f (docker images -q --filter reference=libraries-wagtail --filter before=(docker images -q --filter reference=libraries-wagtail | head -n1 ))
```

We can see more info on minikube's usage with `docker system df` and `docker system prune` lets us remove other objects (containers, volumes) that might be taking up space. But realistically, it is the repeatedly re-built app images which consume the vast majority of disk.

## Tools

**setup.sh** bootstraps the local development environment so we can begin working on the site without needing to push to a remote instance like staging.

**sync.fish** copies a remote instance's data to our local development environment. `./docs/sync.fish --prod --media` does the media files while `./docs/sync.fish --prod --db` does the database. It can sync from either `--stage` or `--prod`. It can also sync media/database between our production and staging instances if we provide _both_ instance flags. Run `./docs/sync.fish --help` for complete usage information.

**dev.fish** starts or stop the local development toolchain (which is: docker, minikube, skaffold). Run `./dev.fish up` or `start` to begin and `./dev.fish down` or `stop` when we're done. Note that this is just a convenience; there's no reason we cannot manage the development tools individually.

**release** increments the latest tag that triggers our CI/CD workflow and pushes the tag to the remote. `./docs/release prod` does a production release. _This script might need to change when we migrate off of Gitlab CI to GitHub_.

## Development Git Flow

Outline:

- Pick an app or feature to work on & checkout a logically-named branch based on the `dev` branch
  - `iss##` for work related to an issue is a fine naming convention
- Start up the local development environment, `./docs/dev.fish up`
- If model or database changes happen, run `makemigrations -n short_name`
  - Try to _always_ name migrations so it's possible infer what it's doing from the filename
  - Combine multiple migrations for the same feature/issue _before pushing to the remote repo_ with `squashmigrations app_name first_number last_number`
  - It is recommended to indicate that a commit requires running migrations, e.g. by appending `(MIGRATE)` to the end of the first line of the commit message
- Feel free to `git push origin $BRANCH` to save intermediary changes to the remote repo
- Once a feature is complete, checkout `dev` & `git merge $BRANCH` into it
- Push the dev branch to a staging instance `git push && git tag lib-ep-$NUM && git push --tags` then test it at libraries-libep.cca.edu
- Merge tested code into the main branch, `git checkout main` & `git merge dev`
- Write release notes in the CHANGELOG.md and check if any of this documentation needs to be updated
- Push changes to production, `git tag release-$NUM && git push && git push --tags`

See deployment.md for more details on deploying to remote instances like staging and production.

### Frontend Development

If you are working on frontend (JS, CSS via SCSS) files with a local Wagtail, the fastest way to get your changes on the running site is to run a `pnpx gulp watch` task on your host laptop in a parallel process to the usuall development (skaffold) tools. Gulp will see you make changes to source files, which triggers a build, gulp builds files directly into the static files directory where Wagtail serves them from, and Skaffold notices the new static files and copies them to the running kubernetes pod without restarting or rebuilding anything.

Due to our two-step build process in the Dockerfile, the application pod does not have node available so you cannot actually compile the static files on it, e.g. by running a shell on the pod and then running gulp.

## Settings, Environment Variables, and Secrets

We use a combination of environment variables, kubernetes secrets, and Google Secret Manager to manage Wagtail configuration. For the most part, the effect of these variables/secrets is felt in the primary settings file [base.py](../libraries/libraries/settings/base.py). The values that control settings are set like so:

- Environment variables are set in the kubernetes deployment files
  - [local configMap](../kubernetes/local/configMap.yml) and [deployment](../kubernetes/local/deployment.yml) files which in turn use a [secrets.env](../kubernetes/local/secrets.env) file
  - [staging](../kubernetes/staging.yaml)
  - [production](../kubernetes/production.yaml)
- Secrets are in k8s, `kubectl -n $NAMESPACE get secrets` lists them & [`k8 decode $SECRET $KEY`](https://github.com/cca/libraries-k8s) can show their values
  - Staging and production use k8s secrets but there's no need to locally
  - Secrets have to be mounted as files or environment variables in the pod
  - We need _at least_ a service account JSON key added as a `GS_CREDENTIALS` env var which is used to authenticate with Secret Manager
- Google Secret Manager is used for particularly confidential settings like the secret key, database URL, and search URL
  - There is a libraries_staging secret in the CCA Web Staging project
  - There is a libraries_production secret in the CCA Web Prod project
  - The same service account which is used for GSB access is used to access these secrets (in a Secret Manager Secret Accessor role)

## Module (including Wagtail) Updates

See [Upgrading Wagtail](https://docs.wagtail.org/en/stable/releases/upgrading.html) but I prefer to use [uv](https://docs.astral.sh/uv/) for dependencies. `uv` is faster and stores a dependency graph rather than a list of unrelated packages like requirements.txt. Upgrade outline:

- Identify target versions to upgrade to (`uv pip list --outdated` helps)
- Read Wagtail [release notes](https://docs.wagtail.org/en/stable/releases/) and make note of any breaking changes
- Upgrade blocking dependencies (e.g. Django, Python itself) in [pyproject.toml](../pyproject.toml), then run `uv lock` to update the lockfile
  - It's best to pin dependencies to a specific version, e.g. `"Django==3.2.8"` rather than `"Django>=3.2.8"`
  - Major Django updates can require database migrations, too
- If there were significant dependency changes, do a full test/release cycle _at least_ on the staging instance
- Make Wagtail changes, e.g. editing module paths or fixing deprecation warnings
- Update Wagtail in the same manner as above (edit pyproject, `uv lock`)
- Run `migrate` on the app pod (using [libraries k8s aliases](https://github.com/cca/libraries-k8s)):

```sh
> set -gx NS lib-production
> k exec (k get pods -o name | grep wagtail) -- python manage.py migrate
```

The upgrade notes say to run `python manage.py makemigrations` before migrate but technically all db migrations should already be included so that step _should_ be necessary. If migrations are needed, the local test server tells us so on startup.

## Installing dependencies locally

We do not need to install the Python dependencies on our host laptop since the app runs in Minikube. However, some `uv` commands (like running `uv pip list --outdated` to find outdated dependencies) expect a functioning virtualenv to exist.

If installing locally, note that `uwsgi` has trouble building against managed python installations, see [this comment](https://github.com/astral-sh/uv/issues/6488#issuecomment-2345417341) for instance. The solution is to set a `LIBRARY_PATH` shell var that points to the "lib" directory of our local python. With `mise` and fish shell, this looks like `set -x LIBRARY_PATH (mise where python)/lib`.

## Static Files

We put _all_ static (CSS, JS) files under the main app's static folder, in libraries/libraries/static. I am not sure if this is a great strategy as it separates apps from their styles (e.g. libraries/exhibitions from libraries/libraries/static/scss/exhibits.scss). Static files are served with the [whitenoise](http://whitenoise.evans.io/en/stable/) middleware add-on.

We use [Gulp](http://gulpjs.com/) for our front-end build tool. Note that tools like autoprefixer are solving some bugs, so switching might result in some style problems (e.g., the radio buttons on the home page search box need autoprefixer).

`npm run` builds the site's assets and `npm watch` watches for changes and rebuilds. See the Gulpfile for more information on these tasks. We should be able to run these tasks on our host laptop and not inside the development app container; the changes will not trigger an image rebuild (which would slow down development terribly) and should be automatically [synced](https://skaffold.dev/docs/pipeline-stages/filesync/) to the container if Skaffold is working properly. Portal takes a different approach to the problem of syncing assets without rebuilding the image and mounts the local application code into the app container as a volume, but this adds complexity to the local kubernetes configuration.

## Media

We have, as of 6/2023, about 4.5gb of media files (images, documents, a few videos) on the Libraries' Wagtail site. All the media are stored in [Google Storage Buckets](https://cloud.google.com/storage/docs/buckets) for all instances (local, staging, production) of the site.

| Instance | GCP Project | GSB
|----------|-------------|----
| Local | CCA Web Staging | libraries-media-local
| Staging | CCA Web Staging | libraries-media-staging-lib-ep
| Production | CCA Web Prod | libraries-lib-production

Some of these may change as we look into using the Autoclass storage feature and using a CDN with the site.

The Wagtail app uses a `GS_BUCKET` env var to know which bucket to use in which context. Each bucket has one service account with a `Storage Object Admin` role that can modify its contents and there is a corresponding `GS_CREDENTIALS` env var that holds the account's JSON key as a string. To run the app locally, save the local bucket's key (it's shared in Dashlane) as kubernetes/local/local-gsb-sa.json.

See the bottom of base.py for how these env vars are used. This is also where we tell Google to set a long-lived cache control header on all objects. This improves performance and our "whitenoise" static file library uses cache busting parameters in file names anyways.

All buckets allow public access (give user `allUsers` the `Storage Object Viewer` role) though it would be difficult to guess the URL of a resource that is not linked off of our websites. Buckets should use **Uniform** and not **Fine-grained** access control on the Permissions tab (as of Wagtail 3.0 / Django 4.0 / django-storages-google 1.14.2).

The CI/CD pipeline does some juggling with media files, copying from _another_ intermediary bucket to the ones that are actually used to serve resources for the website.

## Database Migrations

When a model is changed, we must generate migration files that implement the change in the database. This process is made complicated by the fact that we need to generate the migrations on the (local, minikube) pod running the app. Here is an outline of the process:

```sh
> # make edits to a models.py file
> k8 sh # enter the pod running the app using the `k8` helper
> python manage.py makemigration -n "name_of_feature" # create named migrations
> python manage.py migrate # apply migrations
> exit # leave the pod
> ./docs/get_migrations.fish # copy the migration files off the pod
```

If we test our code after migration and want to make changes, it can get tricky. We'll need to undo the migrations on the local database, delete the migration files, then create new ones. It's important to have a copy of the migration we want to undo. On the pod, we can run `python manage.py migrate {app} {number}` where the number is the one _before_ the change we want to undo. For instance, if we wanted to undo the changes in libraries/blog/migrations/0003_create_blogindex.py we would run `python manage.py migrate blog 0002`.

### Best Practices

Name migrations with the `-n` flag, e.g. `python manage.py makemigrations -n new_feature`.

Remember to **always** [squash](https://docs.djangoproject.com/en/4.0/topics/migrations/#squashing-migrations) and name migrations as noted under the development heading.

Sometimes when we create a model, we want to immediately create an instance of it rather than require the admin to create one manually. This lets us create objects like the site's singular home page or top-level categories programmatically, greatly decreasing the time to bootstrap a new iteration of the site. Here are a few examples of this tactic:

- home/migrations/0002_create_homepage.py
- blog/migrations/0003_create_blogindex.py
- categories/migrations/0006_create_categories.py

Note:

- if we generate child pages, we must make sure the migration lists the migration generating the parent page as a dependency (see how create_categories depends upon create_homepage)
- we can disallow certain page types from being created manually at all if we a) generate them during migrations & b) ensure no other model lists them in its `subpage_types`
- `slug`s must be unique & therefore make a good hook when writing the `remove_xxx` method which undoes the effects of the migration

## Postgres Update

How to update the Postgres version. Example `kubectl` commands do not include the appropriate `-n $NAMESPACE` flags, see [libraries-k8s](https://github.com/cca/libraries-k8s) for the easiest way to account for these. The `psycopg2` library we use supports multiple versions of postgres so you might not need to update it while upgrading the database.

Upgrade local postgres:

```sh
# download the local db
k exec (k8 pod) -- pg_dump --host postgres.libraries-wagtail --user postgres cca_libraries > db.sql
# stop Skaffold (Ctrl + C), delete whole minikube cluster, recreate it (takes a while)
minikube delete
./docs/dev.fish up
# copy postgres db onto app pod & restore it
k cp db.sql (k8 pod):/app
k exec (k8 pod) -- psql -U postgres -f db.sql
```

Upgrade gcloud postgres:

- Export current DB `gcloud sql export sql $INSTANCE $GSB_URI --database $DB_NAME --offload` where `GSB_URI` is a path to a storage bucket and filename like gs://libraries-db-dumps-ci/2023-09-29-libraries-lib-ep-staging.sql.gz
- Cloud Console > SQL > go to the new verion's instance (someone else at CCA should've already created it, if not create it yourself) > Database > Add a database with the same name as the old one
  - Import > Enter the path to the SQL export in GSB and select the new database
  - Users > Add user with the same username and password as the current db
  - Check that the db has content & the user can access it with `gcloud sql connect $INSTANCE --database $DB_NAME --user $USER`
- Edit the Dockerfile line that specifies a Postgres client version, e.g. `apt-get install postgresql-client-14`
- Search & replace references to the old instance e.g. in CI/CD yaml, that's _at least_:
  - /docs/sync.fish `DB_INSTANCE` vars
  - gitlab-ci.yml `gcloud sql databases...` commands
  - kubernetes/*.yaml cloudsqlproxy proxy container's `command` in the `--instance` flag
- (Depending) edit the cloudsqlproxy kubernetes secrets
  - If you changed the db username or password, edit their base64-encoded values. It looks roughly like `kubectl get secret cloudsql-db-credentials -o yaml > secret.yaml; echo 'NEW PASSWORD' | base64 | pbcopy; vim secret.yaml; kubectl apply -f secret.yaml`. Env var secrets like these require a pod restart to take effect.
  - The cloudsql-instance-credentials secret should not need changes, it contains JSON credentials for a service account used during CD but the SA should have access to all Cloud SQL instances in the GCloud project
- When we push a new tagged commit that triggers the GitLab pipelines, it will build the new Docker image with the updated postgres client and recreate the pods giving us any new secrets
- For future use of docs/sync.fish with the new db instance, give the db's service account permission to export to the db dumps storage bucket
  - GCP > Staging or Prod project > SQL > New instance > Copy **Service Account** username off of Overview page
  - GCP > Storage > DB dumps bucket > **Permissions** > **Grant Access** > Add the SA as a new principle with only the Storage Object Creator role

## Elasticsearch

We have separate ES clusters for staging and production. Locally, we run ES without authentication. In the clusters, login with the credentials from Dashlane. Each cluster has a `libraries` user in a `libraries` role which can only access indices with the site's `ES_INDEX_PREFIX` which is in turn the kubernetes namespace of the instance (`lib-ep` for staging, `lib-production` for production). THe role also has `monitor` cluster access, otherwise `GET /` preflight check requests fail.

Migrating Elasticsearch versions is easy compared to Postgres because we can rebuild the index from scratch, we don't need to migrate data. See [isse #54](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/54) which had more steps because it involved switching to authenticated ES but it's these steps:

- Update the local k8s cluster's ES version in kubernetes/local/elasticsearch/deployment.yaml for testing
- Update the `elasticsearch` dependency in pyproject.toml
- Update `WAGTAILSEARCH_BACKENDS` in`libraries/libraries/settings/base.py` to use the new version's backend
- Run `python manage.py update_index` to rebuild the index
- Edit the elasticsearch URL in kubernetes/staging.yaml and then kubernetes/production.yaml

## Miscellaneous Extras

### Sitemap

There are a few layers to the CCA Libraries site. The outline below shows the basic structure with a few annotations:

- The parentheses next to a page's title contain the name of its model
- An asterisk \* denotes a _singleton_ page (e.g. the home page, various indices)
- A caret ^ denotes non-page content (doesn't appear in search results, shouldn't be visited directly in a web browser)

```yaml
Root (Wagtail abstraction)
    |---Home* (home.HomePage)
        |---Services* (categories.CategoryPage)
            |---Instructional Services & Technology^ (categories.RowComponent)
                |---Child content pages...
            |---Circulation Services^ (categories.RowComponent)
                |---Child content pages...
            |---Emerging Projects^ (categories.RowComponent)
                |---Child content pages...
        |---Collections* (categories.CategoryPage)
            |---Collections^ (categories.RowComponent)
                |---Various special collections (categories.SpecialCollectionsPage)
                |---Child content pages...
        |---About Us* (categories.CategoryPage)
            |---About Us^ (categories.RowComponent)
                |---Staff listing* (staff.StaffListPage)
                |---Hours* (hours.HoursPage)
                |---Child content pages...
        |---Blog*^ (blog.BlogIndex)
            |---All blog posts... (blog.BlogPage)
        |---Exhibits* (exhibitions.ExhibitsIndexPage)
            |---All digital exhibitions... (exhibitions.ExhibitPage)
        |---Search (no model, only a view in search/views.py)
        |---Brokenlinks^ (no model, only a view in brokenlinks/views.py)
        |---Instagram^ (instagram.Instagram, used on home page)
        |---Serials Solution API^ (no model, only a view in sersol_api/views.py, used in Koha)
        |---Summon^ (scheduled task to update our deleted catalog records in Summon)
        |---Alerts^ (add alerts with django-admin, they appear in the header)
```

The grandchild pages of each main category (Services, Collections, and About Us), represented above with the phrase "child content pages...", can use one of three page models: ServicePage, AboutUsPage, and SpecialCollectionsPage. Each of these pages can then, in turn, have children of any of those three types.

### Wagtail 2.0 / Django 2.0 update

We will likely not need to revisit this but several things changed and the upgrade process wasn't _quite_ straightforward so it's worth documenting a few things. Here was my basic process after updating the Wagtail dependency:

```sh
> wagtail updatemodulepaths
> python manage.py migrate
> python manage.py collectstatic
```

- update `django.core.urlresolvers` to `django.urls` wherever it occurs
- delete `django.contrib.auth.middleware.SessionAuthenticationMiddleware` from the `MIDDLEWARE` setting if it's present; it was removed in Django 2.0
- if urls.py has the line `url(r'^django-admin/', include(admin.site.urls))` the `include()` method can be removed such that it's simply "admin.site.urls"
- look for uses of `models.ForeignKey` which don't specify the now-required `on_delete` parameter

Useful docs:

- http://docs.wagtail.io/en/v2.0/releases/2.0.html#upgrade-considerations
- https://docs.djangoproject.com/en/2.0/releases/2.0/
