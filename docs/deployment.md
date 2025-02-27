# Deployment

Deployment is done with GitHub Actions and triggered by tags in the format ENVIRONMENT-TYPE-NUMBER, e.g. `stg-deploy-6`.

- `stg-deploy-N` -> https://libraries-libep.cca.edu/
- `prod-deploy-N` -> https://libraries.cca.edu (production)

The [./docs/release](./release) script makes things even easier. It automatically increments the last deploy tag, pushes to GitHub, and watches the action run. It deploys to staging by default and passing `prod` to it deploys to production.

Note that _the git branch does not matter_; GitHub will happily deploy a tagged commit to production even if it's not on the `main` branch. The full procedure to publsh changes looks like:

```sh
> git commit -m "here are my changes"
> git push # push changes to remote
> git tag $TAG # create a tag hooked to one of the deployments above
> git push origin $TAG # push the tag, triggering a deployment
> gh run watch # (optional) monitor deployment progress
```

Building images without deploying can be done separately with `stg-build-N` or `prod-build-N`.

To watch the process of a build or see why it failed, visit [GitHub's **Actions** page](https://github.com/cca/libraries_wagtail/actions/).

The build/deploy tags are ephemeral and serve no purpose other than triggering actions. They can be deleted remotely or locally after they've served their purpose, but there's also no need to delete them.

## Website Releases

We _also_ have version tags that look like `v5.0.0`. These match versions in [our changelog](./CHANGELOG.md) and are decoupled from the deployment tags. They vaguely track our Wagtail version (the major version of each should match). To do a full release:

- Write release notes in [the changelog](./CHANGELOG.md)
- Post in Slack that you're doing a release and whether downtime is anticipated (it's usually not)
- Run `./docs/release prod`
  - Does a deployment with the next `prod-deploy` tags
  - Creates a v2.3.4 version tag matching the version in changelog
  - Creates [a release on GitHub](https://github.com/cca/libraries_wagtail/releases) with generated notes from the last version tag
- Add the changelog section to the GitHub release notes
- Copy/paste the GitHub notes into \#libraries Slack channel

## Service Account Setup

See the [Service Account setup script](./service-acct-setup.fish) for one-time setup procedures needed to allow GitHub Actions to authenticate to GCP and perform actions like pushing an image or running kubernetes commands on our cluster. We should just be able to edit the variables at the top of the script to create the necessary Service Account and Workload Identity Pool for a new environment (this is how the production setup was created). These steps are mostly documented in the google-github-actions/auth repo under the section [Workload Identity Federation through a Service Account](https://github.com/google-github-actions/auth?tab=readme-ov-file#indirect-wif). Note that we cannot use Direct Workload Identity Federation because of how Docker auth works.
