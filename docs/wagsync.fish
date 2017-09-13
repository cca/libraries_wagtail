#!/usr/bin/env fish

set local_wagtail '/Users/ephetteplace/Code/libraries-wagtail'
set remote_wagtail '/opt/libraries_wagtail'
set static_destination "$local_wagtail/libraries/media"
set dbname 'libraries_cca_edu'
set dt (date "+%Y-%m-%d")
set pw 'This is not the actual password :)'

cd $static_destination
rsync -avz --progress --delete live:$remote_wagtail/libraries/media/documents .
rsync -avz --progress --delete live:$remote_wagtail/libraries/media/original_images .
rsync -avz --progress --delete live:$remote_wagtail/libraries/media/images .

# dump SQL db & download
# can create a .pgpass file in user's home folder to bypass password prompt
# (except this doesn't seem to work on pg 9.5)
# https://www.postgresql.org/docs/current/static/libpq-pgpass.html
echo 'password is on your clipboard, paste at the prompt'
echo $pw | pbcopy
ssh live "pg_dump -Fc -h vm-postgres-04.cca.edu -U libuser -d $dbname > $HOME/$dt.dump.sql"

rsync -avz --progress live:~/$dt.dump.sql $static_destination

# overwrite current postgres db
# NOTE: first time through, run `createuser libuser` too
pg_restore -c -h localhost -U libuser -d $dbname $static_destination/(dt).dump.sql

# reset everyone's passwords to 'password' for local development
python $local_wagtail/libraries/manage.py pw_reset
