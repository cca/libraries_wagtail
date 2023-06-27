# Libraries Wagtail Site

This folder contains the generic documentation for the CCA Libraries Wagtail site as well as development scripts, all of which are meant to be run from the parent directory. Most of the site's apps also have readme files with more information specific to them.

## Questions & Todos

- [ ] serving media files locally (mount libraries/media somehow or use another GSB)
- [x] commands for pruning minikube's docker instance (see bottom of section below)

## Running Wagtail Locally

We need docker, minikube, kubectl, and skaffold. Many of these are available from different places but they're also all on homebrew. The other sensible place to get these tools is as [gcloud](https://cloud.google.com/sdk/docs/install) CLI components, which we need to interact with our cloud-hosted resources (databases, static files, servers) anyways. To use them, we make sure that the "bin" subfolder inside the gcloud tools is on our path.

```sh
> brew i kubectl minikube skaffold # kubectl is a dependeny of homebrew minikube
> brew i --cask docker # Docker Desktop app
> # OR use gcloud for these two components
> gcloud components install kubectl minikube skaffold
```

Docker Desktop provides nice visualizations of resources (images, volumes) as well as a set of command-line completions for the most popular shells. We may need to give it additional resources under Settings > Resources.

Minikube can also be configured to use more resources than the defaults:

```sh
> minikube config set vm-driver docker
> minikube config set cpus 4
> minikube config set memory 8192
```

Once we're set up, the dev.fish script should do everything we need. Notes below are for troubleshooting or work on our development tooling.

To start:

1. Open Docker Desktop & wait for it to start the docker daemon
2. Run `minikube start` & wait for it to complete
  a. _if we don't have the site's database yet_ run `skaffold -p db-only` and `./docs/sync.fish`
3. Run `skaffold dev --trigger polling --port-forward` to build the cluster's servers & reload when we change files, see `skaffold help` for other options such as "build", "debug", and "run"

There are three ways to forward a port on the minikube cluster so we can open the website using our localhost domain in a browser:

1. (easiest) run `skaffold dev` with the `--port-forward` flag. The [port-forward](https://skaffold.dev/docs/pipeline-stages/port-forwarding/) configuration is in Skaffold.yml. If we omit this from the Skaffold profile but use the `--port-forward` flag, Skaffold will automatically create forwarding for all services, but if the pods are recreated it will not recreate the forwarding, so this is not recommended.
2. Run `kubectl -n libraries-wagtail port-forward service/libraries 8000:8000`, this is what Skaffold does behind the scenes
3. Use [Kube Forwarder.app](https://kube-forwarder.pixelpoint.io/) (install it with `brew install --cask kube-forwarder`) which provides a GUI interface around port forwarding

`minikube dashboard` opens a nice web UI to visualize its k8s resources.

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
> docker images
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

If you are working on frontend (JS, CSS via SCSS) files with a local Wagtail, the fastest way to get your changes on the running site is to run a `gulp watch` task on your host laptop in a parallel process to the usuall development (skaffold) tools. Gulp will see you make changes to source files, which triggers a build, gulp builds files directly into the static files directory where Wagtail serves them from, and Skaffold notices the new static files and copies them to the running kubernetes pod without restarting or rebuilding anything.

Due to our two-step build process in the Dockerfile, the application pod does not have node available so you cannot actually compile the static files on it, e.g. by running a shell on the pod and then running gulp.

## Module (including Wagtail) Updates

I prefer to use [pipenv](https://pipenv.pypa.io/en/latest/) for python development as it stores an actual dependency graph rather than a list of unrelated packages like requirements.txt. For instance, if package A is changed to no longer rely on package B, pipenv removes B from the graph, but requirements doesn't know anything about dependencies and will happily continue to install a useless piece of software. Eventually, we might move to using pipenv in the Dockerfile, but for now we can `pipenv install wagtail=3.0.0` to add or upgrade a package and then `pipenv run pip freeze -l > libraries/requirements.txt` to flatten the pipenv graph into a requirements list.

Wagtail, and often Django, updates require running a few extra steps on the app pod:

```sh
> alias k 'kubectl -nlibraries-wagtail' # save a lot of typing
> k exec (k get pods -o name | grep wagtail) -- /app/libraries/manage.py migrate
```

## Static Files

We put _all_ static (CSS, JS) files under the main app's static folder, in libraries/libraries/static. I am not sure if this is a great strategy as it separates apps from their styles (e.g. libraries/exhibitions from libraries/libraries/static/scss/exhibits.scss). Static files are served with the [whitenoise](http://whitenoise.evans.io/en/stable/) middleware add-on.

We use [Gulp](http://gulpjs.com/) for our front-end build tool. Note that tools like autoprefixer are solving some bugs, so switching might result in some style problems (e.g., the radio buttons on the home page search box need autoprefixer).

`npm run` builds the site's assets and `npm watch` watches for changes and rebuilds. See the Gulpfile for more information on these tasks. We should be able to run these tasks on our host laptop and not inside the development app container; the changes will not trigger an image rebuild (which would slow down development terribly) and should be automatically [synced](https://skaffold.dev/docs/pipeline-stages/filesync/) to the container if Skaffold is working properly. Portal takes a different approach to the problem of syncing assets without rebuilding the image and mounts the local application code into the app container as a volume, but this introduces some complexity into the local kubernetes configuration.

There are two folders under the main static directory ("moodle" and "summmon") for hosting static files used in external services that cannot host their own content. The Summon files are contained within this project (see libraries/summon and the summon Gulp tasks) while the Moodle files are created in the [Moodle Styles](https://github.com/cca/moodle-styles) project.

## Database Migrations

When a model is changed, we must generate migration files that implement the change in the database. This process is made complicated by the fact that we need to generate the migrations on the (local, minikube) pod running the app. Here is an outline of the process:

```sh
> # make edits to a models.py file
> k8 sh # enter the pod running the app using the `k8` helper
> cd libraries; python manage.py makemigration -n "name_of_feature" # create migrations
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
