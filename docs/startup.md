# Starting a Wagtail site

Here's the basic steps to starting this project. We'll assume you're in the root of the project (e.g. the parent of this "docs" directory).

```sh
> # create a virtual environment using the python3 interpreter
> virutalenv -p python3 .
> # activate the environment—you'll do this every time you want to work on the project
> # use "activate.fish" below for Fish shel
> source bin/activate
> # install Wagtail & other dependencies in the environment's packages
> pip install -r requirements.txt
```

# When you're done

```sh
> # if you've added or updated packages, save the updates for pip
> pip freeze > requirements.txt
> # turn off the virtualenv
> deactivate
```
