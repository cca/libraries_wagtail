# Deployment

Deployment is triggered by tags of a certain format.

- `ep-full-$TAG` -> https://libraries-libep.cca.edu/
- `mg-full-$TAG` -> https://libraries-libmg.cca.edu/
- `release-$TAG` -> https://libraries.cca.edu (production)

First push the commits you want, then remember to `git push --tags` to push up the tag or else a deployment won't be triggered.

Right now, we only have `full` builds that do everything but eventually we might have more focused builds that don't take as long.

To watch the process of a build or see why it failed, visit GitLab's **Pipelines** page under CI/CD: https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/pipelines
