#!/usr/bin/env bash
virtualenv -p python3 .
source bin/activate
pip install -r libraries/requirements.txt
npm install
npm run build
python libraries/manage.py migrate
python libraries/manage.py createsuperuser
source bin/activate
python libraries/manage.py runserver

