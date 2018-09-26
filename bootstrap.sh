#!/usr/bin/env bash

# python & virtualenv setup
virtualenv -p python3 .
source bin/activate
pip install -r libraries/requirements.txt

# build frontend assets
command -v nvm && nvm install
npm install
npm run build

# postgres setup
createuser libuser
createdb libraries_cca_edu --owner libuser

# wagtail setup
python libraries/manage.py migrate
python libraries/manage.py createsuperuser
python libraries/manage.py createcachetable

# run dev server
python libraries/manage.py runserver
