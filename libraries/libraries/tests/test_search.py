from datetime import date

from blog.models import BlogIndex, BlogPage
from django.core.management import call_command
from exhibitions.models import ExhibitPage, ExhibitsIndexPage

from .base import CMSPageTestCase
from .utils import PageFactory, create_test_image


class SearchPageTests(CMSPageTestCase):
    """Tests for search functionality."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create searchable pages with unique content
        cls.blog_index = PageFactory.create_page(
            BlogIndex,
            parent=cls.home,
            title="News",
            search_description="Library news and announcements",
            published=True,
        )
        cls.blog_post = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="Unique Testing Blog Post About Libraries",
            date=date(2026, 4, 1),
            main_image=create_test_image(),
            search_description="A blog post for testing search functionality",
            published=True,
        )
        cls.exhibits_index = PageFactory.create_page(
            ExhibitsIndexPage,
            parent=cls.home,
            title="Exhibitions",
            search_description="Library exhibitions and displays",
            published=True,
        )
        cls.exhibit = PageFactory.create_page(
            ExhibitPage,
            parent=cls.exhibits_index,
            title="Searchable Exhibit About Archives",
            search_description="An exhibit for testing search functionality",
            published=True,
        )
        # Must update search index after creating pages
        call_command("update_index", skip_checks=False, verbosity=0)

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

    def test_summon_redirect_without_query(self):
        """Test that default search redirects to Summon without following."""
        response = self.client.get("/search/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://cca.summon.serialssolutions.com/")

    def test_summon_redirect_with_query(self):
        """Test that 'all' searchType redirects to Summon with query."""
        response = self.client.get("/search/?searchType=all&q=test", follow=False)
        self.assertEqual(response.status_code, 301)  # permanent redirect
        self.assertIn("cca.summon.serialssolutions.com", response.url)
        self.assertIn("q=test", response.url)

    def test_catalog_redirect(self):
        """Test that catalog searchType redirects to Koha."""
        response = self.client.get("/search/?searchType=catalog&q=test", follow=False)
        self.assertEqual(response.status_code, 301)
        self.assertIn("library.cca.edu/cgi-bin/koha", response.url)
        self.assertIn("q=test", response.url)

    def test_services_search_returns_results(self):
        """Test that services search returns actual pages."""
        response = self.client.get("/search/?searchType=services&q=Libraries")
        self.assertEqual(response.status_code, 200)
        self.assertIn("search_results", response.context)
        # Blog post title contains "Libraries"
        results = response.context["search_results"]
        result_ids = [p.id for p in results]
        self.assertIn(self.blog_post.id, result_ids)

    def test_services_search_content_in_response(self):
        """Test that search results appear in rendered HTML."""
        response = self.client.get("/search/?searchType=services&q=Testing")
        self.assertEqual(response.status_code, 200)
        # Django's assertContains checks both status and content
        self.assertContains(response, "Unique Testing Blog Post")

    def test_search_pagination(self):
        """Test that search results are paginated at 10 items per page."""
        # Create 12 searchable blog posts to trigger pagination
        for i in range(12):
            PageFactory.create_page(
                BlogPage,
                parent=self.blog_index,
                title=f"Pagination Test Post Number {i}",
                date=date(2026, 3, i + 1),
                main_image=create_test_image(),
                search_description=f"Pagination test post {i} for search testing",
                published=True,
            )
        # Must update search index after creating pages
        call_command("update_index", skip_checks=False, verbosity=0)

        # Search for all the pagination posts
        response = self.client.get("/search/?searchType=services&q=Pagination")
        self.assertEqual(response.status_code, 200)
        results = response.context["search_results"]

        # Check pagination
        self.assertTrue(results.has_other_pages())
        self.assertEqual(len(results), 10)  # 10 per page
        self.assertTrue(results.has_next())

        # Test page 2
        response_page2 = self.client.get(
            "/search/?searchType=services&q=Pagination&page=2"
        )
        results_page2 = response_page2.context["search_results"]
        self.assertEqual(len(results_page2), 2)  # remaining 2 posts

    def test_search_pagination_invalid_page(self):
        """Test that invalid page numbers are handled gracefully."""
        # Invalid page number (non-integer) should default to page 1
        response = self.client.get("/search/?searchType=services&q=Test&page=invalid")
        self.assertEqual(response.status_code, 200)
        results = response.context["search_results"]
        self.assertEqual(results.number, 1)

        # Page number too high should return last page
        response = self.client.get("/search/?searchType=services&q=Test&page=9999")
        self.assertEqual(response.status_code, 200)
        results = response.context["search_results"]
        self.assertEqual(results.number, results.paginator.num_pages)

    def test_search_no_results(self):
        """Test search with query that returns no results."""
        response = self.client.get(
            "/search/?searchType=services&q=zzzzznonexistentquery"
        )
        self.assertEqual(response.status_code, 200)
        results = response.context["search_results"]
        self.assertEqual(len(results), 0)
