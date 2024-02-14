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
\tnot delete any local files, it merely fills in the ones you're missing."
    echo -e "\nExamples:"
    echo -e "\tsync.fish -s — sync the staging database locally"
    echo -e "\tsync.fish -s --db --media — sync the staging database and media locally"
    echo -e "\tsync.fish --prod --media — download production media (but not the database)"
    echo -e "\tsync.fish --prod --stage --db — sync production database to staging"
    echo -e "\n'Staging' here refers to Eric's libraries-libep.cca.edu site and its related
database and media files, NOT Mark's libraries-libmg.cca.edu site. If we feel a need
to differentiate, we can use three instance flags instead of the current two."
    echo -e "You can sync the prod db or media to staging by providing _both_ instance
flags. This is always a unidirectional sync from prod to staging."
    exit 0
end

function activate_config
    # no need to activate if the current config is already set
    if test -f ~/.config/gcloud/active_config
        set -g CURRENT_CONFIG (cat ~/.config/gcloud/active_config)
        if test $argv[1] = $CURRENT_CONFIG
            return
        end
    end
    gcloud config configurations activate $argv[1] >/dev/null
    or begin
        echo "Error: unable to activate $argv[1] gcloud configuration; does it exist?
    Check with 'gcloud config configurations list' and if it does not exist
    create it (see docs/setup.sh for details)." 1>&2
        exit 1
    end
end

# these are consistent across all projects
set REGION us-west1-b
set DB_INSTANCE psql14-instance
# these are used in 2 places cuz of prod-to-staging db sync
set STAGE_DB_NAME libraries-lib-ep
set STAGE_DB_GSB gs://libraries-db-dumps-ci

if set -q _flag_p
    echo "Using production context"
    set CTX production
    set -gx GOOGLE_CLOUD_QUOTA_PROJECT cca-web-0
    activate_config production
    set DB_NAME libraries-lib-production
    set DB_GSB gs://cca-manual-db-dumps
    set MEDIA_GSB gs://libraries-lib-production
else if set -q _flag_s
    echo "Using staging context"
    set CTX staging
    set -gx GOOGLE_CLOUD_QUOTA_PROJECT cca-web-staging
    activate_config staging
    set DB_NAME $STAGE_DB_NAME
    set DB_GSB $STAGE_DB_GSB
    set MEDIA_GSB gs://libraries-media-staging-lib-ep
else
    set_color --bold red
    echo "You must specify either the -s/--stage or -p/--prod context."
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

# Sync media
if set -q _flag_m
    if set -q _flag_p
        # sync prod cloud storage to staging
        echo -e "\nOpening Google Cloud Transfer Service; run the existing job for syncing libraries media"
        open "https://console.cloud.google.com/transfer/jobs?project=cca-web-0"
    else
        # implies --stage flag, sync staging media to local cloud storage
        # we can use rsync because these buckets are under the same project
        echo "Syncing staging media to the bucket used during local development.
This sync is additive; no files in the local bucket will be deleted."
        gsutil -m rsync -r $MEDIA_GSB gs://libraries-media-local
    end
end

function export_db
    set -g DB_FILE (date "+%Y-%m-%d")-$DB_NAME.sql.gz
    set -g DB_URI $DB_GSB/$DB_FILE
    gcloud sql export sql $DB_INSTANCE $DB_URI --database $DB_NAME
end

# Sync database
if set -q _flag_d;
    or not set -q _flag_m

    if set -q _flag_p; and set -q _flag_s
        # sync prod db to staging
        export_db
        # copy db file from a prod GSB to a staging one
        gsutil cp $DB_URI $STAGE_DB_GSB
        echo "Switching to staging context"
        activate_config staging
        gcloud sql databases delete $STAGE_DB_NAME --instance $DB_INSTANCE
        gcloud sql databases create $STAGE_DB_NAME --instance $DB_INSTANCE
        # we can't use DB_URI because it points to the prod GSB
        gcloud sql import sql $DB_INSTANCE $STAGE_DB_GSB/$DB_FILE --database $STAGE_DB_NAME
    else
        # remote to local minikube database sync
        if not minikube status >/dev/null
            set_color --bold red
            echo "minikube isn't runnning, try running 'minikube start' first" 1>&2
            set_color normal
            exit 1
        end
        # configure kubectl context
        echo "Updating minikube and kubectl context"
        minikube update-context
        kubectl config set-context --current --namespace libraries-wagtail

        set WAG_POD (kubectl get pods --selector=app=libraries -o=custom-columns=:metadata.name --sort-by=.metadata.creationTimestamp --no-headers -n libraries-wagtail)
        if test -n "$WAG_POD"
            echo "The Wagtail pod is running; Postgres will refuse to drop and recreate the database
while a user is connected. Stop Skaffold, or run the 'db-only' profile, and attempt
this command again." 1>&2
            exit 1
        end

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

        # Export database to GSB and then download it, copy to pod, and restore.
        # We delete cloudsql users to prevent errors when the export is restored.
        export_db
        gsutil cp $DB_URI .
        echo "Using $PG_POD to restore $DB_NAME from $DB_FILE"
        kubectl -n libraries-wagtail cp ./$DB_FILE $PG_POD:/tmp/$DB_FILE
        kubectl -n libraries-wagtail exec $PG_POD -- sh -c "\
        dropdb -U postgres cca_libraries;\
        createdb -U postgres cca_libraries;\
        zcat /tmp/$DB_FILE \
        | sed -E -e '/cloudsqladmin|cloudsqlsuperuser/d' \
        | psql -U postgres cca_libraries;"
    end
end
