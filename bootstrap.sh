#!/usr/bin/env bash

# python & virtualenv setup
pipenv shell --three
pipenv install

# install node (using either nvm or n) & build frontend assets
command -v nvm >/dev/null && nvm install
command -v n >/dev/null && n stable
npm install
npm run build

# postgres setup
createuser libuser
createdb libraries_cca_edu --owner libuser

# wagtail setup
python libraries/manage.py migrate
python libraries/manage.py createsuperuser
python libraries/manage.py createcachetable

# imagemagick needed for animated GIF support
if test $(uname) = 'Darwin'; then
    brew install imagemagick
elif test $(uname) = 'Linux'; then
    sudo apt-get install libmagickwand-dev
fi

echo 'Copy libraries/libraries/settings/local.py.template to local.py and edit it accordingly.'
