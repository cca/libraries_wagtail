"""Base test classes and utilities for CMS page tests."""

from django.http import HttpResponse
from django.test import Client
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage


class CMSPageTestCase(WagtailPageTestCase):
    """
    Base test case for testing Wagtail CMS pages.

    Extends WagtailPageTestCase which provides specialized assertions for
    testing page routability, renderability, editability, and parent/child
    relationships. Also includes custom utilities for testing page loading,
    status codes, and content rendering without requiring external services.
    
    Creates a HomePage in setUpTestData that can be used as a parent for other
    pages that require parent_page_types = ["home.HomePage"].
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create root page
        cls.root = Page.get_first_root_node()
        
        # Create a test image for the HomePage background
        from .utils import create_test_image
        test_bg_image = create_test_image(name="home_background.png", size=(1440, 630))
        
        # Create HomePage under root for tests that need it as a parent
        cls.home = HomePage(title="Home", background_image=test_bg_image)
        cls.root.add_child(instance=cls.home)
        cls.home.save_revision().publish()
        
        # Update the default Site to point to our HomePage
        site = Site.objects.get(is_default_site=True)
        site.root_page = cls.home
        site.save()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def get_page_by_slug(self, slug: str):
        """
        Get a page by its slug path.

        Args:
            slug: The URL slug/path to the page (e.g., 'about/' or 'services/contact/')

        Returns:
            The Page object if found, None otherwise
        """
        try:
            return Page.objects.get(slug=slug).specific
        except Page.DoesNotExist:
            return None

    def get_page_url(self, page: Page) -> str | None:
        """
        Get the full URL path for a page.

        Args:
            page: A Wagtail Page object (can be specific instance)

        Returns:
            The URL path for the page
        """
        return page.get_url()

    def assert_page_loads(
        self, page_url: str, expected_status: int = 200
    ) -> HttpResponse:
        """
        Assert that a page loads successfully and return the response.

        Args:
            page_url: The URL path to test
            expected_status: The expected HTTP status code (default: 200)

        Returns:
            The response object for further testing

        Raises:
            AssertionError if the page doesn't load with the expected status
        """
        response = self.client.get(page_url)
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Page {page_url} returned {response.status_code}, expected {expected_status}",
        )
        return response

    def assert_page_contains(self, page_url: str, content: str) -> None:
        """
        Assert that a page loads and contains expected content.

        Args:
            page_url: The URL path to test
            content: The content string to look for in the response

        Raises:
            AssertionError if the page doesn't load or doesn't contain the content
        """
        response = self.assert_page_loads(page_url)
        self.assertContains(
            response,
            content,
            msg_prefix=f"Content '{content}' not found on page {page_url}",
        )

    def assert_page_not_contains(self, page_url: str, content: str) -> None:
        """
        Assert that a page loads but does NOT contain specific content.

        Args:
            page_url: The URL path to test
            content: The content string that should NOT be in the response

        Raises:
            AssertionError if the page doesn't load or contains the unexpected content
        """
        response = self.assert_page_loads(page_url)
        self.assertNotContains(
            response,
            content,
            msg_prefix=f"Content '{content}' should not be found on page {page_url}",
        )

    def assert_page_context(self, page_url: str, context_key: str) -> None:
        """
        Assert that a page's template context contains a specific key.

        Args:
            page_url: The URL path to test
            context_key: The context variable key to check for

        Raises:
            AssertionError if the context key is not present
        """
        response = self.assert_page_loads(page_url)
        self.assertIn(
            context_key,
            response.context,
            f"Context key '{context_key}' not found in page {page_url}",
        )


class CMSSetupMixin:
    """Mixin for common CMS test setup and teardown operations."""

    def create_test_page(self, parent: Page | None = None, **kwargs) -> Page:
        """
        Create a test page under the given parent.

        Args:
            parent: Parent page (defaults to root if None)
            **kwargs: Additional fields to set on the page

        Returns:
            The created Page instance
        """
        if parent is None:
            parent = Page.get_root_nodes().first()  # type: ignore
            assert parent is not None, "Root page must exist to create test pages"

        page = Page(title=kwargs.pop("title", "Test Page"), **kwargs)
        parent.add_child(instance=page)
        page.save()
        return page

    def publish_page(self, page: Page) -> Page:
        """
        Publish a page so it's visible on the live site.

        Args:
            page: The page to publish

        Returns:
            The page instance
        """
        page.save_revision().publish()
        return page
