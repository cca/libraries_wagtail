#!/usr/bin/env bash

local_wagtail='/Users/ephetteplace/Code/libraries_wagtail'
remote_wagtail='/opt/libraries_wagtail'
static_destination="$local_wagtail/libraries/media"
mkdir $static_destination 2>/dev/null
db='libraries_cca_edu'
user='$user'
dt=$(date "+%Y-%m-%d")
pw='This is not the actual password :)'

# NOTE: assumes an ssh alias of "live" for the production instance
cd $static_destination
rsync -avz --progress --delete live:${remote_wagtail}/libraries/media/documents .
rsync -avz --progress --delete live:${remote_wagtail}/libraries/media/original_images .
rsync -avz --progress --delete live:${remote_wagtail}/libraries/media/images .
cd ..
rsync -avz --progress --delete live:${remote_wagtail}/libraries/static/fonts libraries/static

# dump SQL db & download
echo 'password is on your clipboard, paste at the prompt'
echo $pw | pbcopy
ssh live "pg_dump -Fc -h vm-postgres-04.cca.edu -U $user -d ${db} > ${HOME}/${dt}.dump.sql"

rsync -avz --progress live:~/$dt.dump.sql $static_destination

# overwrite db, first time through we need to ensure user & db exist
createuser $user 2>/dev/null
createdb $db 2>/dev/null
pg_restore --clean -h localhost -U $user -d ${db} ${static_destination}/${dt}.dump.sql

# reset everyone's passwords to 'password' for local development
python ${local_wagtail}/libraries/manage.py pw_reset
