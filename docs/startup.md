# Starting a Wagtail site

Here's the basic steps to starting this project. We'll assume you're in the root of the project (e.g. the parent of this "docs" directory). See [the Wagtail "getting started" doc](http://docs.wagtail.io/en/v1.10.1/getting_started/tutorial.html) for more. There's a "bootstrap.sh" script that does all this.

```sh
> # create a virtual environment using the python3 interpreter
> virtualenv -p python3 .
> # activate the environment—you'll do this every time you want to work on the project
> # use "activate.fish" below for Fish shell
> source bin/activate
> # install Wagtail & other dependencies in the environment's packages
> pip install -r libraries/requirements.txt
> # install npm dependencies (used for front-end build processes)
> npm install
> # build/minify the frontend assets
> npm run build
> # create the site database & an admin user
> python libraries/manage.py migrate
> python libraries/manage.py createsuperuser
```

# When you're done

```sh
> # if you've added or updated packages, write them into libraries/requirements.txt
> # turn off the virtualenv
> deactivate
```
