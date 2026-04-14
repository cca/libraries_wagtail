from .base import CMSPageTestCase


class SearchPageTests(CMSPageTestCase):
    """Tests for search functionality."""

    def test_search_page_loads(self):
        """Test that the search page loads."""
        self.assert_page_loads("/search/?searchType=services")

    def test_search_with_empty_query(self):
        """Test search with no query parameters."""
        response = self.client.get("/search/?searchType=services")
        self.assertEqual(response.status_code, 200)
        # By default, search redirects to Summon
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 302)

    # TODO test services vs other searches
    # TODO test pagination
    # TODO test that an actual result is return (create test page then retrieve it)
    # TODO summon search should redirect but do not actually load Summon URL if possible, can the test client be told not to follow redirects?
