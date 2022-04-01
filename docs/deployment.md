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

Right now, we only have `full` builds that do everything but eventually we might have more focused builds that don't take as long. We should focus on making the Docker image as cacheable as possible to increase speed.

To watch the process of a build or see why it failed, visit GitLab's **Pipelines** page under CI/CD: https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/pipelines
