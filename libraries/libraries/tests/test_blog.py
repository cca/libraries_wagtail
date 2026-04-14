"""
Tests for blog pages.

This module tests both the BlogIndex page and individual BlogPage posts,
including navigation between posts (next/previous).

Test Fixtures:
- BlogIndex page under HomePage
- 3 BlogPage posts with different dates (Jan 5, Feb 10, Mar 15, 2026)
- Each post has a test image and is published

The fixtures are duplicated in both test classes to keep them independent.
"""

from datetime import date

from blog.models import BlogIndex, BlogPage

from .base import CMSPageTestCase, CMSSetupMixin
from .utils import PageFactory, create_test_image

# Blog


class BlogIndexPageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for the blog index page with published blog posts."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create BlogIndex as a child of HomePage (cls.home from CMSPageTestCase)
        cls.blog_index = PageFactory.create_page(
            BlogIndex,
            parent=cls.home,  # Explicitly set parent to HomePage
            title="Blog",
            search_description="Library News",
            published=True,
        )

        # Create test images for blog posts
        cls.image1 = create_test_image(name="blog1.png", size=(700, 467))
        cls.image2 = create_test_image(name="blog2.png", size=(700, 467))
        cls.image3 = create_test_image(name="blog3.png", size=(700, 467))

        # Create 3 blog posts with different dates (newest first in variable names)
        # Post 3 is newest, Post 1 is oldest
        cls.blog_post_3 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="Latest News Post",
            search_description="The most recent library news",
            date=date(2026, 3, 15),
            main_image=cls.image3,
            published=True,
        )

        cls.blog_post_2 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="Second News Post",
            search_description="Middle library news post",
            date=date(2026, 2, 10),
            main_image=cls.image2,
            published=True,
        )

        cls.blog_post_1 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="First News Post",
            search_description="Oldest library news post",
            date=date(2026, 1, 5),
            main_image=cls.image1,
            published=True,
        )

    def test_blog_index_page_is_routable(self):
        """Test that the blog index page can be accessed via URL."""
        self.assertPageIsRoutable(self.blog_index)

    def test_blog_index_page_is_renderable(self):
        """Test that the blog index page renders without errors."""
        self.assertPageIsRenderable(self.blog_index)

    def test_blog_index_page_title(self):
        """Test that the blog index page has the correct title."""
        self.assertEqual(self.blog_index.title, "Blog")

    def test_blog_index_serves_latest_post(self):
        """Test that BlogIndex serves the latest blog post."""
        blog_index_url = self.blog_index.get_url()
        assert blog_index_url is not None
        response = self.client.get(blog_index_url)
        self.assertEqual(response.status_code, 200)
        # Verify that the context contains the latest post (blog_post_3)
        self.assertEqual(response.context["page"], self.blog_post_3)
        # Verify the page title in the response
        self.assertContains(response, "Latest News Post")

    def test_blog_index_includes_latest_five(self):
        """Test that BlogIndex context includes up to 5 latest posts."""
        blog_index_url = self.blog_index.get_url()
        assert blog_index_url is not None
        response = self.client.get(blog_index_url)
        self.assertEqual(response.status_code, 200)
        # Verify latest_posts context variable exists
        self.assertIn("latest_posts", response.context)
        latest_posts = response.context["latest_posts"]
        # We have 3 posts, so all should be in the latest_posts list
        self.assertEqual(len([p for p in latest_posts if p is not None]), 3)
        # Verify they're in reverse chronological order (newest first)
        self.assertEqual(latest_posts[0], self.blog_post_3)
        self.assertEqual(latest_posts[1], self.blog_post_2)
        self.assertEqual(latest_posts[2], self.blog_post_1)


class BlogPageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for individual blog pages and their navigation."""

    @classmethod
    def setUpTestData(cls):
        """Reuse the same fixtures as BlogIndexPageTests."""
        super().setUpTestData()
        # Create BlogIndex as a child of HomePage
        cls.blog_index = PageFactory.create_page(
            BlogIndex,
            parent=cls.home,
            title="Blog",
            search_description="Library News",
            published=True,
        )

        # Create test images for blog posts
        cls.image1 = create_test_image(name="blog1.png", size=(700, 467))
        cls.image2 = create_test_image(name="blog2.png", size=(700, 467))
        cls.image3 = create_test_image(name="blog3.png", size=(700, 467))

        # Create 3 blog posts with different dates (newest first in variable names)
        # Post 3 is newest, Post 1 is oldest
        cls.blog_post_3 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="Latest News Post",
            search_description="The most recent library news",
            date=date(2026, 3, 15),
            main_image=cls.image3,
            published=True,
        )

        cls.blog_post_2 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="Second News Post",
            search_description="Middle library news post",
            date=date(2026, 2, 10),
            main_image=cls.image2,
            published=True,
        )

        cls.blog_post_1 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            title="First News Post",
            search_description="Oldest library news post",
            date=date(2026, 1, 5),
            main_image=cls.image1,
            published=True,
        )

    def test_blog_page_is_routable(self):
        """Test that individual blog pages can be accessed via URL."""
        self.assertPageIsRoutable(self.blog_post_1)
        self.assertPageIsRoutable(self.blog_post_2)
        self.assertPageIsRoutable(self.blog_post_3)

    def test_blog_page_is_renderable(self):
        """Test that individual blog pages render without errors."""
        self.assertPageIsRenderable(self.blog_post_1)
        self.assertPageIsRenderable(self.blog_post_2)
        self.assertPageIsRenderable(self.blog_post_3)

    def test_blog_page_with_required_fields(self):
        """Test that blog pages have required fields set correctly."""
        # Test blog_post_3 (latest)
        self.assertEqual(self.blog_post_3.title, "Latest News Post")
        self.assertEqual(self.blog_post_3.date, date(2026, 3, 15))
        self.assertIsNotNone(self.blog_post_3.main_image)

        # Test blog_post_1 (oldest)
        self.assertEqual(self.blog_post_1.title, "First News Post")
        self.assertEqual(self.blog_post_1.date, date(2026, 1, 5))
        self.assertIsNotNone(self.blog_post_1.main_image)

    def test_blog_page_context_has_navigation(self):
        """Test that blog pages have navigation context (latest_posts, next_post, previous_post)."""
        # Test middle post (blog_post_2)
        blog_post_2_url = self.blog_post_2.get_url()
        assert blog_post_2_url is not None
        response = self.client.get(blog_post_2_url)
        self.assertEqual(response.status_code, 200)

        # Verify navigation context exists
        self.assertIn("latest_posts", response.context)
        self.assertIn("next_post", response.context)
        self.assertIn("previous_post", response.context)

        # Verify latest_posts contains our posts
        latest_posts = response.context["latest_posts"]
        self.assertIn(self.blog_post_1, latest_posts)
        self.assertIn(self.blog_post_2, latest_posts)
        self.assertIn(self.blog_post_3, latest_posts)

    def test_newest_post_has_no_next(self):
        """Test that the newest blog post has no next post (next_post=None)."""
        blog_post_3_url = self.blog_post_3.get_url()
        assert blog_post_3_url is not None
        response = self.client.get(blog_post_3_url)
        self.assertEqual(response.status_code, 200)
        # Newest post should have no "next" (newer) post
        self.assertIsNone(response.context["next_post"])
        # But should have a previous (older) post
        self.assertEqual(response.context["previous_post"], self.blog_post_2)

    def test_oldest_post_has_no_previous(self):
        """Test that the oldest blog post has no previous post (previous_post=None)."""
        blog_post_1_url = self.blog_post_1.get_url()
        assert blog_post_1_url is not None
        response = self.client.get(blog_post_1_url)
        self.assertEqual(response.status_code, 200)
        # Oldest post should have no "previous" (older) post
        self.assertIsNone(response.context["previous_post"])
        # But should have a next (newer) post
        self.assertEqual(response.context["next_post"], self.blog_post_2)

    def test_middle_post_has_both_navigation(self):
        """Test that a middle blog post has both next and previous navigation."""
        blog_post_2_url = self.blog_post_2.get_url()
        assert blog_post_2_url is not None
        response = self.client.get(blog_post_2_url)
        self.assertEqual(response.status_code, 200)
        # Middle post should have both next (newer) and previous (older) posts
        self.assertEqual(response.context["next_post"], self.blog_post_3)
        self.assertEqual(response.context["previous_post"], self.blog_post_1)
