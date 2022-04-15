# Summon (or other discovery layer) Broken Links app

This app receives POSTed information and sends it to a Google Spreadsheet for analysis. It records the OpenURL, Summon permalink, and Summon content type of the item with the broken link as well as an email and open-ended comments field from the user reporting the broken link. To configure this app:

1. create a Google Form with fields for each of the data listed above
2. make sure it can be submitted by _anyone_ not just your particular institution
3. view the form and copy its URL, changing the last path component to "formResponse" e.g. `https://docs.google.com/forms/d/e/{{key}}/formResponse`
4. put the URL into a settings file (e.g. libraries/settings/base.py) with name `BROKENLINKS_GOOGLE_SHEET_URL`
5. find the ID values of each input, like "entry.123123123", easiest way to do this is to create a prefilled link then look in the URL for where it's filling in your values
6. enter those into the `BROKENLINKS_HASH` setting
7. insert the included JavaScript into Summon, double-checking the URLs

See the Summon app for the custom JavaScript that's inserted into Summon that POSTs data back to this app.

## Submitting Cases to Vendor Support

The [Libraries' Tampermonkey scripts](https://github.com/cca/libraries_tampermonkey) includes a useful one for Summon that aids in turning our users' broken link reports into a support tickets. The Summon script provides two interfaces for our JavaScript console: a `report()` function for generating informative support ticket text and a `docs` array exposing all the search results data.

Running `report()` with no arguments in our console presents a dialog window of preformatted text to copy and then opens the URL for the[ProQuest Support Center](https://support.proquest.com/). We can paste the text into the body of the ticket to provide generic details like the article's Summon bookmark and its OpenURL. Usually, we want to submit the ticket to Ex Libris, who maintain Summon and CDI. However, sometimes a content provider is at fault. For instance, if Summon has accurate metadata but a link to an EBSCO database fails because the article should be there but is missing, then we should submit the ticket (using the copied report text) to EBSCO instead.

Note that `report()` is intended for use with a Summon bookmark where there is only one search result displayed.

The `docs` array exposes the complete underlying data of Summon search results, much of which is not visible in the user interface. Summon stores the query in this data structure too, and sometimes "best bets", so the first search result is often at the `docs[1]` index and not `docs[0]` as we would expect. There's _a ton_ of data in the record which helps us to determine how Summon is linking to the full text. Some informative pieces are:

- a series of booleans like `has_fulltext` and `is_scholarly` that are used in Summon's facets
- the `open_url` minus our link resolver's prefix
- `link_to_html`, `uris`, `dois`, `iedl_dbids`, `pqids` are all properties that indicate a direct (not OpenURL) link
- `content_type` maps to Summon's list of record types and its associated facet
- `link_provider`, `source_types`, and `databases` tell us where the metadata/content comes from

The `docs` array does not refresh when we perform filtering or repeat searches in the same tab. To update the `docs`, refresh the page.

Here is a complete example of a Summon doc:

```js
{
    "bookmark": "eNrjYmDJy89LZWHgNDSwMNM1NzC14GDgKi7OMjAwMDWzMOdk4PN1jPD0DfVV8PQNcHQO4WFgKSkqTeWFUNwMGm6uIc4eugVF-YWlqcUl8bmZxcmpOTmJean5pcXxRmYGpkam5ibmFsYkKAUACwUpnA",
    "has_fulltext": true,
    "is_fulltext_hit": false,
    "in_holdings": true,
    "is_scholarly": false,
    "is_peer_reviewed": false,
    "is_print": false,
    "open_url": "ctx_ver=Z39.88-2004&ctx_enc=info%3Aofi%2Fenc%3AUTF-8&rfr_id=info%3Asid%2Fsummon.serialssolutions.com&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&rft.genre=article&rft.atitle=MAXIMUM+IMPACT&rft.jtitle=Artforum+international&rft.au=Kaelen+Wilson-Goldie&rft.date=2021-09-01&rft.pub=Artforum+Inc&rft.issn=1086-7058&rft.volume=60&rft.issue=1&paramdict=en-US",
    "link": "https://cca.summon.serialssolutions.com/2.0.0/link/0/eLvHCXMwY2AwNtIz0EUrE1KMgA2JRGDVkGRmlmZhaZpkDmzmmgPrNtNEYB8MfOysa6S5b5CpW6glbHEhaGsMNLphpSS46E7JTwaNmuuDWuLABGdibmFfUKgLukcKNN8KvVSDmYHV0MTcFHSavq-RP2LRhxn4yjzQ9UK65gamFhglMLhacRNgSIe5ALymWg-ypgToW6R11rADGylypyCDAOwkaQVHSFoRYmBKzRNm4A7LLC5NzAGJFoswSNvkJhZl2_k6Rnj6hvoqePoGODqH2OiDBUUZNNxcQ5w9dGHWxwOTCGjcPzEvNb-0OB7hAGMxBpa8_LxUCQYF42RDi2TwDbgGSSYGySkWRilJlslGwN6PeVpaYmKaJIMiQeOkiFAjzcBlBFoGAl6WJcPAUlJUmirLwAwMSjlw1AAAfdqjQA",
    "link_to_html": "https://cca.summon.serialssolutions.com/2.0.0/link/0/eLvHCXMwY2AwNtIz0EUrE1KMgA2JRGDVkGRmlmZhaZpkDmzmmgPrNtNEYB8MfOysa6S5b5CpW6hlBPTY7WLoKktYEQkut1Pyk0FD5vqgZjgwtZmYWzAzsJqYArsNoGV7Rv6I5R1m4MvxQBcJ6ZobmFpglLXgCsRNgCEQZhd49bQeZPUI0F9IK6phRzMS6SJBBgHY6dAKjpD4F2JgSs0TZuAOyywuTcwBiRaLMEjb5CYWZdv5OkZ4-ob6Knj6Bjg6h9jogwVFGTTcXEOcPXRhdsUDox00lp-Yl5pfWhyPsM1YjIElLz8vVYJBwTjZ0CIZfKutQZKJQXKKhVFKkmWyEbBHY56WlpiYJsmgSNA4KSLUSDNwGYGWdoCXWskwsJQUlabKMjADA00OHAkAwZ2R2w",
    "link_provider": "ProQuest",
    "id": "FETCH-proquest_miscellaneous_26052574783",
    "merged_id": "FETCHMERGED-proquest_miscellaneous_26052574783",
    "thumbnail_small": "https://syndetics.com/index.aspx?isbn=/sc.gif&issn=1086-7058&client=calcolarts",
    "thumbnail_medium": "https://syndetics.com/index.aspx?isbn=/mc.gif&issn=1086-7058&client=calcolarts",
    "thumbnail_large": "https://syndetics.com/index.aspx?isbn=/lc.gif&issn=1086-7058&client=calcolarts",
    "content_type": "Magazine Article",
    "content_types": [
        "Magazine Article"
    ],
    "subject_terms": [
        "19th century",
        "Art galleries & museums",
        "Books",
        "Curators",
        "Painting",
        "Paints",
        "Visual artists"
    ],
    "source_types": [
        "Aggregation Database"
    ],
    "languages": [
        "English"
    ],
    "uris": [
        "https://search.proquest.com/docview/2605257478"
    ],
    "issns": [
        "1086-7058"
    ],
    "title": "<mark>MAXIMUM IMPACT</mark>",
    "full_title": "<mark>MAXIMUM IMPACT</mark>",
    "snippet": "Ouattara’s exhibition history—in galleries and in significant institutional group shows—has been continuous, but the major, contextualizing museum surveys have...",
    "publishers": [
        "Artforum Inc"
    ],
    "publisher": "Artforum Inc",
    "publication_title": "Artforum international",
    "publication_places": [
        "New York"
    ],
    "abstracts": [
        {
            "abstract": "Ouattara’s exhibition history—in galleries and in significant institutional group shows—has been continuous, but the major, contextualizing museum surveys have not yet materialized. Several are done on wooden panels heavy with textured pigments, using a range of nails, screws, hinges, and brackets to incorporate beams, tablets, picture frames, shapes like ears that extrude from upper corners, paper shopping bags, burlap sacks, coils of wire, old photographs, and whole books, such as the one (Albert Einstein on relativity) stuck to the middle of OZB, 1993, exhibited that same year in Susan Vogel and Ousmane Sow’s “Fusion: West African Artists at the Venice Biennale.” The curators Defne Ayas and Natasha Ginwala—who selected four canvases from the past decade for “Minds Rising, Spirits Tuning,” their joint exhibition for the Thirteenth Gwangju Biennale, which was held this past spring after a seven-month delay—were especially drawn to the rhythmic and cosmological dimensions of Ouattara’s work and the ways in which his paintings are the outcome of a sustained spiritual practice. Sartre urged him to return to painting, which he did, eventually becoming a crucial mentor for a generation of artists arriving to France from all over Asia, Africa, and South America in the ’70s and ’80s. Because Yankel had spent time in West Africa, he was pivotal for a group of students who came to",
            "attribution": "Alt-PressWatch (Alumni Edition)"
        }
    ],
    "copyrights": [
        "Copyright Artforum Inc. Sep 2021"
    ],
    "publication_years": [
        "2021"
    ],
    "genres": [
        "Feature"
    ],
    "disciplines": [
        "Visual Arts"
    ],
    "volumes": [
        "60"
    ],
    "issues": [
        "1"
    ],
    "web_of_science": {},
    "scopus_references_count": 0,
    "pqids": [
        "2605257478"
    ],
    "ssids": [
        "ssj0005687"
    ],
    "iedl_dbids": [
        "M2O"
    ],
    "from_library": false,
    "is_a_i": false,
    "fulltext_link": "https://cca.summon.serialssolutions.com/2.0.0/link/0/eLvHCXMwY2AwNtIz0EUrE1KMgA2JRGDVkGRmlmZhaZpkDmzmmgPrNtNEYB8MfOysa6S5b5CpW6glbHEhaGsMNLphpSS46E7JTwaNmuuDWuLABGdibmFfUKgLukcKNN8KvVSDmYHV0MTcFHSavq-RP2LRhxn4yjzQ9UK65gamFhglMLhacRNgSIe5ALymWg-ypgToW6R11rADGylypyCDAOwkaQVHSFoRYmBKzRNm4A7LLC5NzAGJFoswSNvkJhZl2_k6Rnj6hvoqePoGODqH2OiDBUUZNNxcQ5w9dGHWxwOTCGjcPzEvNb-0OB7hAGMxBpa8_LxUCQYF42RDi2TwDbgGSSYGySkWRilJlslGwN6PeVpaYmKaJIMiQeOkiFAjzcBlBFoGAl6WJcPAUlJUmirLwAwMSjlw1AAAfdqjQA",
    "publication_date": "09/2021",
    "authors": [
        {
            "fullname": "Kaelen Wilson-Goldie",
            "$$hashKey": "object:315"
        }
    ],
    "editors": [],
    "corporate_authors": [],
    "peer_documents": [],
    "libguides": [],
    "cited_by_id": [],
    "cited_by_doi": [],
    "cited_by_isbn": [],
    "cites_id": [],
    "cites_doi": [],
    "cites_isbn": [],
    "index": 1,
    "hasDetailPage": false,
    "databases": [],
    "buttons": [],
    "display_thumbnail": false,
    "$$hashKey": "object:178",
    "_hasAltmetric": false
}
```
