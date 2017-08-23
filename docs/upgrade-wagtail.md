# How to Upgrade Wagtail

I've found upgrading Wagtail to be a little less straightforward than I thought, probably because of our server configuration more than anything. Here's what I've had to do:

- `pip install --upgrade wagtail` locally to test the new version
- once ready, `pip freeze > libraries/requirements.txt` and then `git commit`
- on the production server, `sudo bash; workon libraries` to enter the libraries virtualenv as root
- `git pull` to get repo updates and `pip install -r libraries/requirements.txt` to update Wagtail
- at this point, the live version of the site is still running on the old Wagtail code
- restart the gunicorn server (`service supervisord stop; sleep 2; service supervisord start`)
- but the static files for new admin modules aren't available!?!
- wipe out the old static files `rm -rf static`
- collect the new ones `python libraries/manage.py collectstatic`
- insert them into the repo's static dir `rsync -avz static libraries`

All those final steps around static files feel wonky but that's what's worked for me.
