"""
Tests for exhibition pages.

This module tests both ExhibitsIndexPage and individual ExhibitPage exhibits,
including pagination and the featured exhibit functionality.

Test Fixtures:
- ExhibitsIndexPage under HomePage
- 3 ExhibitPage exhibits with header images
- Each exhibit is published and has required fields

The fixtures follow the same pattern as blog tests for consistency.
"""

from exhibitions.models import ExhibitPage, ExhibitsIndexPage, HeaderImage

from .base import CMSPageTestCase, CMSSetupMixin
from .utils import PageFactory, create_test_image


class ExhibitsIndexPageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for the exhibitions index page with published exhibits."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create ExhibitsIndexPage as a child of HomePage
        cls.exhibitions = PageFactory.create_page(
            ExhibitsIndexPage,
            parent=cls.home,
            title="Exhibitions",
            search_description="Library Exhibitions",
            published=True,
        )

        # Create test images for exhibits
        cls.image1 = create_test_image(name="exhibit1.png", size=(1360, 900))
        cls.image2 = create_test_image(name="exhibit2.png", size=(1360, 900))
        cls.image3 = create_test_image(name="exhibit3.png", size=(1360, 900))

        # Create 3 exhibits
        cls.exhibit_1 = PageFactory.create_page(
            ExhibitPage,
            parent=cls.exhibitions,
            title="First Exhibit",
            search_description="The first library exhibit",
            published=True,
        )
        # Add header image to exhibit_1
        HeaderImage.objects.create(page=cls.exhibit_1, image=cls.image1, sort_order=0)

        cls.exhibit_2 = PageFactory.create_page(
            ExhibitPage,
            parent=cls.exhibitions,
            title="Second Exhibit",
            search_description="The second library exhibit",
            featured=True,  # This one is featured
            published=True,
        )
        # Add header image to exhibit_2
        HeaderImage.objects.create(page=cls.exhibit_2, image=cls.image2, sort_order=0)

        cls.exhibit_3 = PageFactory.create_page(
            ExhibitPage,
            parent=cls.exhibitions,
            title="Third Exhibit",
            search_description="The third library exhibit",
            published=True,
        )
        # Add header image to exhibit_3
        HeaderImage.objects.create(page=cls.exhibit_3, image=cls.image3, sort_order=0)

    def test_exhibitions_index_is_routable(self):
        """Test that the exhibitions index page can be accessed via URL."""
        self.assertPageIsRoutable(self.exhibitions)

    def test_exhibitions_index_is_renderable(self):
        """Test that the exhibitions index page renders without errors."""
        self.assertPageIsRenderable(self.exhibitions)

    def test_exhibitions_index_includes_exhibits(self):
        """Test that the exhibitions index displays all published exhibits."""
        exhibitions_url = self.exhibitions.get_url()
        assert exhibitions_url is not None
        response = self.client.get(exhibitions_url)
        self.assertEqual(response.status_code, 200)
        # Verify exhibits context variable exists
        self.assertIn("exhibits", response.context)
        exhibits_page = response.context["exhibits"]
        # All 3 exhibits should be in the list
        exhibit_list = list(exhibits_page)
        self.assertEqual(len(exhibit_list), 3)
        # Verify they're ordered by most recent first
        self.assertIn(self.exhibit_3, exhibit_list)
        self.assertIn(self.exhibit_2, exhibit_list)
        self.assertIn(self.exhibit_1, exhibit_list)


class ExhibitPageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for individual exhibit pages."""

    @classmethod
    def setUpTestData(cls):
        """Create test fixtures for exhibit pages."""
        super().setUpTestData()
        # Create ExhibitsIndexPage
        cls.exhibitions = PageFactory.create_page(
            ExhibitsIndexPage,
            parent=cls.home,
            title="Exhibitions",
            search_description="Library Exhibitions",
            published=True,
        )

        # Create test images
        cls.image1 = create_test_image(name="exhibit1.png", size=(1360, 900))
        cls.image2 = create_test_image(name="exhibit2.png", size=(1360, 900))

        # Create exhibits
        cls.exhibit_1 = PageFactory.create_page(
            ExhibitPage,
            parent=cls.exhibitions,
            title="Art & Design Exhibit",
            search_description="A showcase of student art and design work",
            display_template="banner",
            gallery_columns=2,
            published=True,
        )
        HeaderImage.objects.create(page=cls.exhibit_1, image=cls.image1, sort_order=0)

        cls.exhibit_2 = PageFactory.create_page(
            ExhibitPage,
            parent=cls.exhibitions,
            title="Featured Photography",
            search_description="Featured photography from the archives",
            display_template="foursquare",
            gallery_columns=3,
            featured=True,
            published=True,
        )
        HeaderImage.objects.create(page=cls.exhibit_2, image=cls.image2, sort_order=0)

    def test_exhibit_page_is_routable(self):
        """Test that individual exhibit pages can be accessed via URL."""
        self.assertPageIsRoutable(self.exhibit_1)
        self.assertPageIsRoutable(self.exhibit_2)

    def test_exhibit_page_is_renderable(self):
        """Test that individual exhibit pages render without errors."""
        self.assertPageIsRenderable(self.exhibit_1)
        self.assertPageIsRenderable(self.exhibit_2)

    def test_exhibit_has_header_image(self):
        """Test that exhibits have header images."""
        self.assertEqual(self.exhibit_1.header_image.count(), 1)
        self.assertEqual(self.exhibit_2.header_image.count(), 1)
        # Verify the images are the ones we created
        self.assertEqual(self.exhibit_1.header_image.first().image, self.image1)
        self.assertEqual(self.exhibit_2.header_image.first().image, self.image2)

    def test_featured_exhibit(self):
        """Test that the featured flag works correctly."""
        self.assertFalse(self.exhibit_1.featured)
        self.assertTrue(self.exhibit_2.featured)

    def test_exhibit_display_templates(self):
        """Test that different display templates are set correctly."""
        self.assertEqual(self.exhibit_1.display_template, "banner")
        self.assertEqual(self.exhibit_2.display_template, "foursquare")

    def test_exhibit_gallery_settings(self):
        """Test that gallery settings are configured."""
        self.assertEqual(self.exhibit_1.gallery_columns, 2)
        self.assertEqual(self.exhibit_2.gallery_columns, 3)
