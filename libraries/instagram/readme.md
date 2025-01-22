# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. Instagram has changed their underlying API _many_ times on us, necessitating repeated rewrites of this code. For now, we pull JSON straight from Instagram without using an API (see [#168](https://github.com/cca/libraries_wagtail/issues/166)).

We should consider a way to disable this app and display something else on the home page (a random image?) during periods when it is broken and we won't be able to fix it in a timely manner.

## Usage

Instagram appears to block data center IP addresses, if we try to run this whole process on the server we receive a `401` unauthorized response with some JSON about needing to login. So instead we run a local script [ig.fish](./ig.fish) which downloads JSON from Instagram, uploads it to a running pod based on the `NS` env var, and runs the `instagram` management command which creates a new `Instagram` object. We may want to run the script locally as a cron job:

```sh
# cronjob to run at 2pm every weekday and logs to cron.log in our home directory
0 14 * * 1-5 NS=lib-production cd /path/to/wagtail && ./libraries/instagram/ig.fish 2&>> ~/cron.log
```

We should regularly review ig.fish. It uses an internal app ID that might change and we may also want to update the User Agent header to be a more current version.
