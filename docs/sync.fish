#!/usr/bin/env fish
# see Portal > scripts/portaldev-copy-db and portaldev-copy-media

argparse -n sync.fish --exclusive 's,p' s/stage p/prod h/help d/db m/media -- $argv
if set -q _flag_h
    echo "Synchronize local environment with the libraries site media and/or Postgres database
from either the staging or production instances. Options:"
    echo -e "\t-s, --stage\tuse the staging cluster (default)"
    echo -e "\t-p, --prod\tuse the production cluster (mutually exclusive with the above)"
    echo -e "\t-d, --db\tsynchronize the database (default)"
    echo -e "\t-m, --media\tsynchronize the media files (images, videos, documents)"
    echo -e "\nExamples:"
    echo -e "\tsync.fish — sync the staging database locally"
    echo -e "\tsync.fish --db --media — sync the staging database and media locally"
    echo -e "\tsync.fish --prod --media — sync production media (but not the database) locally"
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
else
    echo "Using staging context"
    set CTX staging
    set PROJECT cca-web-staging
    set CLUSTER ccaedu-stg
    set DB_INSTANCE cca-edu-staging-2
    set DB_NAME libraries-lib-ep
    set DB_GS_BUCKET gs://libraries-db-dumps-ci
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

# @TODO Sync media
if set -q _flag_m
    set_color --bold red
    echo "Media syncing not implemented yet, skipping..."
    set_color normal
end

# Sync database
if set -q _flag_d;
    or not set -q _flag_m

    if not minikube status >/dev/null
        set_color --bold red
        echo "minikube isn't runnning, try running 'minikube start' first"
        set_color normal
        exit 1
    # configure cluster and gcloud contexts
    minikube update-context
    kubectl config set-context --current --namespace=libraries-wagtail

    # is Postgres pod running?
    set PG_POD (kubectl get pods --selector=app=postgres -o=custom-columns=:metadata.name --sort-by=.metadata.creationTimestamp --no-headers -n libraries-wagtail | tail -n 1)
    if test -z "$PG_POD"
        set_color --bold red
        echo "The Postgres pod is not running in minikube. Run 'skaffold run -p db-only' to start it.'"
        set_color normal
        exit 1
    else
        echo "Found Postgres pod $PG_POD"
    end

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
