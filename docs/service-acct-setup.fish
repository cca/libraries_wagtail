#!/usr/bin/env fish
set PROJECT_ID gcp-project-name
set SA libraries-wagtail-gh-actions
set SERVICE_ACCOUNT_EMAIL $SA@$PROJECT_ID.iam.gserviceaccount.com
set GAR_LOCATION gcp-us-location
set GAR_REPO name-of-repo
set GITHUB_REPO cca/libraries_wagtail

# create a Service Account (SA)
gcloud iam service-accounts create $SA --project $PROJECT_ID

# create a workload identity pool
gcloud iam workload-identity-pools create github \
    --project=$PROJECT_ID \
    --location=global \
    --display-name="GitHub Actions Pool"

# create workload identity pool provider, could use different display name
# ! assumes repository organization is CCA
gcloud iam workload-identity-pools providers create-oidc libraries-wagtail \
    --project=$PROJECT_ID \
    --location="global" \
    --workload-identity-pool="github" \
    --display-name="My GitHub repo Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition="assertion.repository_owner == 'cca'" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# this is the WORKLOAD_IDENTITY_PROVIDER in the workflow
gcloud iam workload-identity-pools providers describe libraries-wagtail \
    --project=$PROJECT_ID \
    --location="global" \
    --workload-identity-pool="github" \
    --format="value(name)"

# Unique ID used below like "projects/1234/locations/global/workloadIdentityPools/github"
set WORKLOAD_IDENTITY_POOL (gcloud iam workload-identity-pools describe github \
    --project=$PROJECT_ID \
    --location="global" \
    --format="value(name)")

# Allow authentications from the Workload Identity Pool to our SA
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/$WORKLOAD_IDENTITY_POOL/attribute.repository/$GITHUB_REPO"

# give SA permission to write to Artifact Registry
gcloud artifacts repositories add-iam-policy-binding $GAR_REPO \
    --project=$PROJECT_ID \
    --location=$GAR_LOCATION \
    --role="roles/artifactregistry.writer" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL"

# Grant GKE-specific roles: container.clusterViewer allows reading cluster information, container.developer permits deploying workloads to the cluster. Also artifactregistry.reader is indeed needed to pull images but writer above should cover that.
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/container.clusterViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/container.developer"
