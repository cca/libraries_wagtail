# Deployment

Deployment is triggered by tags of a certain format.

- `ep-full-$TAG` -> https://libraries-libep.cca.edu/
- `mg-full-$TAG` -> https://libraries-libmg.cca.edu/
- `release-$TAG` -> https://libraries.cca.edu (production)

Note that _the git branch does not matter_; GitLab will happily deploy a commit that's tagged `release-0.0.1` to production even if it's not on the `main` branch. The full procedure to publsh changes looks like:

```sh
> git commit -m "here are my changes"
> git push # push changes to gitlab
> git tag $TAG # create a tag hooked to one of the deployments above
> git push --tags # push the tag, triggering a deployment
> glab ci status --live # (optional) monitor deployment progress
```

Deployments to production ("release" tag) must be manually triggered inside GitLab.

Right now, we only have `full` builds that do everything but eventually we might have more focused builds that don't take as long.

To watch the process of a build or see why it failed, visit GitLab's **Pipelines** page under CI/CD: https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/pipelines

We _also_ have version tags that look like `v5.0.0`. These match versions in [our changelog](./CHANGELOG.md) and are decoupled from the deployment tags. They vaguely track out Wagtail version (the major version of each should match). See below for the full website release process.

## Doing a Website Release

Be careful running `./docs/release` while we are stuck in a bifurcated github/gitlab setup (with CI running on gitlab). Be aware of whether you're on a github or gitlab branch before doing anything. The _deployment_ release tag only matters to gitlab and the _version_ tag only matters to github.

Steps:

- Write release notes in the changelog
- Post in Slack that you're doing a release but no downtime is anticipated
- `./docs/release prod` does the following (you can read it and run steps ad hoc):
  - Do a deployment with one of the release-1.2.3 tags
  - Create a v2.3.4 version tag matching the version in changelog
  - Create a release on github with generated notes from the last version tag
- Edit the github notes with the changelog section
- Copy/paste the github notes into Slack
