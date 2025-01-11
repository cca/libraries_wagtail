# Proxy for Serials Solution API

The Serials Solution XML API does not allow itself to be requested from client-side JavaScript, plus XML is rather hard to work with, so this very small app proxies requests (which come from Koha, see [this file in our snippets project](https://github.com/cca/koha_snippets/blob/main/catalog-js/serials-solutions-holdings.js)), converts them to a dict with xmltodict (it's the sole use of this dependency), and finally returns JSON.

To test, try these URLs:

- https://libraries-libep.cca.edu/sersol/?issn=2162-2574
- https://libraries-libep.cca.edu/sersol/?issn=0172-7028
