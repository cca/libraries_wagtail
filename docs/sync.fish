#!/usr/bin/env fish
# see Portal > scripts/portaldev-copy-db and portaldev-copy-media

argparse -n sync.fish s/stage p/prod h/help d/db m/media -- $argv
if set -q _flag_h
    echo "Synchronize local environment with the libraries site media and/or Postgres database
from either the staging or production instances. Options:"
    echo -e "\t-s, --stage\tuse the staging cluster"
    echo -e "\t-p, --prod\tuse the production cluster"
    echo -e "\t-d, --db\tsynchronize the database (default)"
    echo -e "\t-m, --media\tdownload media files (images, videos, documents). This does
\t\tnot delete any local files, it merely fills in the ones you're missing."
    echo -e "\nExamples:"
    echo -e "\tsync.fish -s — sync the staging database locally"
    echo -e "\tsync.fish --db --media — sync the staging database and media locally"
    echo -e "\tsync.fish --prod --media — download production media (but not the database)"
    echo -e "\tsync.fish --prod --stage --db — sync production database to staging"
    echo -e "\n'Staging' here refers to Eric's libraries-libep.cca.edu site and its related
database and media files, NOT Mark's libraries-libmg.cca.edu site. If we feel a need
to differentiate, we can use three instance flags instead of the current two."
    echo -e "You can sync the prod db or media to staging by providing _both_ instance
flags. This is always a unidirectional sync from prod to staging."
    exit 0
end

set REGION us-west1-b

if set -q _flag_p
    echo "Using production context"
    set CTX production
    set PROJECT cca-web-0
    set CLUSTER ccaedu-prod
    set DB_INSTANCE cca-edu-prod-1
    set DB_NAME libraries-lib-production
    set DB_GS_BUCKET gs://cca-manual-db-dumps
    set MEDIA_GS_BUCKET gs://libraries-lib-production
else if set -q _flag_s
    echo "Using staging context"
    set CTX staging
    set PROJECT cca-web-staging
    set CLUSTER ccaedu-stg
    set DB_INSTANCE cca-edu-staging-2
    set DB_NAME libraries-lib-ep
    set DB_GS_BUCKET gs://libraries-db-dumps-ci
    set MEDIA_GS_BUCKET gs://libraries-media-staging-lib-ep
else
    set_color --bold red
    echo "You must specify either the --stage or --prod context."
    set_color normal
    exit 1
end

set AUTH_USER (gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
set SQL_INSTANCE (gcloud sql instances describe $DB_INSTANCE 2>/dev/null)
if test -n "$AUTH_USER" -a -n "$SQL_INSTANCE"
    echo "Already logged into GCP"
else
    echo "Authenticating with Google"
    gcloud auth login
end

gcloud config set project $PROJECT

# Sync media
if set -q _flag_m
    if set -q _flag_p; and set -q _flag_m
        # sync the two remote cloud storage buckets
        echo -e "\nOpening Google Cloud Transfer Service; run the existing job for syncing libraries media"
        open "https://console.cloud.google.com/transfer/jobs?project=cca-web-0"
    else
        if [ ! -d libraries/media ]
            set_color --bold red
            echo "Error: unable to find libraries/media folder to sync media into."
            echo "Make sure you're running ./docs/sync.sh from the root of this project"
            set_color normal
            exit 1
        end
        # remote to local media sync
        gsutil -m rsync -r $MEDIA_GS_BUCKET libraries/media
    end
end

# Sync database
if set -q _flag_d;
    or not set -q _flag_m

    if set -q _flag_p; and set -q _flag_s
        echo "prod to staging db sync not implemented yet..."
        exit 0
    else
        # remote to local minikube database sync
        if not minikube status >/dev/null
            set_color --bold red
            echo "minikube isn't runnning, try running 'minikube start' first"
            set_color normal
            exit 1
        end
        # configure kubectl context
        minikube update-context
        kubectl config set-context --current --namespace=libraries-wagtail

        # is Postgres pod running?
        set PG_POD (kubectl get pods --selector=app=postgres -o=custom-columns=:metadata.name --sort-by=.metadata.creationTimestamp --no-headers -n libraries-wagtail | tail -n 1)
        while test -z "$PG_POD"
            set_color --bold red
            echo "The Postgres pod is not running in minikube. Running 'skaffold run -p db-only' to start it.'"
            set_color normal
            skaffold run -p db-only
            or echo "Error running skaffold, exiting..." and exit 1
            set PG_POD (kubectl get pods --selector=app=postgres -o=custom-columns=:metadata.name --sort-by=.metadata.creationTimestamp --no-headers -n libraries-wagtail | tail -n 1)
        end
        echo "Found Postgres pod $PG_POD"

        # export database to GS bucket and then download it
        # should I use gs://cca-manual-db-dumps when in prod context?
        set DB_FILE (date "+%Y-%m-%d")-$DB_NAME-$CTX.sql.gz
        set DB_URI $DB_GS_BUCKET/$DB_FILE
        gcloud sql export sql $DB_INSTANCE $DB_URI --database=$DB_NAME
        gsutil cp $DB_URI .
        echo "Using $PG_POD to restore $DB_NAME from $DB_FILE"
        kubectl cp ./$DB_FILE $PG_POD:/tmp/$DB_FILE
        kubectl exec $PG_POD -- sh -c "\
        dropdb -U postgresadmin cca_libraries;\
        createdb -U postgresadmin cca_libraries;\
        zcat /tmp/$DB_FILE \
        | sed -E -e '/cloudsqladmin|cloudsqlsuperuser/d' \
        | psql -U postgresadmin cca_libraries;"
    end
end
