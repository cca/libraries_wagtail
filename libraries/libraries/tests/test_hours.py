"""
Tests for hours page.

This module tests the HoursPage which displays library hours.

Test Fixtures:
- CategoryPage under HomePage
- RowComponent under CategoryPage
- HoursPage under RowComponent (singleton)

The hierarchy is: CategoryPage → RowComponent → HoursPage
"""

from categories.models.pages import CategoryPage, RowComponent
from hours.models import HoursPage

from .base import CMSPageTestCase, CMSSetupMixin
from .utils import PageFactory, create_test_image


class HoursPageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for hours page."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create the required parent hierarchy
        # HoursPage parent must be RowComponent
        cls.category_page = PageFactory.create_page(
            CategoryPage,
            parent=cls.home,
            title="About Us",
            search_description="About the Libraries",
            published=True,
        )

        cls.row = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Hours & Locations",
            summary="<p>Visit us</p>",
            published=True,
        )

        # Create test image for hours page
        cls.image = create_test_image(name="hours.png", size=(230, 115))

        # Create HoursPage as child of RowComponent
        cls.hours_page = PageFactory.create_page(
            HoursPage,
            parent=cls.row,
            title="Hours",
            intro="<p>Library hours</p>",
            main_image=cls.image,
            published=True,
        )

    def test_hours_page_is_routable(self):
        """Test that the hours page can be accessed via URL."""
        self.assertPageIsRoutable(self.hours_page)

    def test_hours_page_is_renderable(self):
        """Test that the hours page renders without errors."""
        self.assertPageIsRenderable(self.hours_page)

    def test_hours_page_loads(self):
        """Test that the hours page loads successfully."""
        hours_url = self.hours_page.get_url()
        assert hours_url is not None
        response = self.assert_page_loads(hours_url)
        # Verify hours context is present (even if empty for test)
        self.assertIn("hours", response.context)

    def test_hours_page_hierarchy(self):
        """Test that hours page is properly nested in the hierarchy."""
        # Hours page parent should be RowComponent
        hours_parent = self.hours_page.get_parent()
        assert hours_parent is not None
        self.assertEqual(hours_parent.specific_class, RowComponent)
        # RowComponent parent should be CategoryPage
        row_parent = self.row.get_parent()
        assert row_parent is not None
        self.assertEqual(row_parent.specific_class, CategoryPage)

    def test_hours_page_singleton(self):
        """Test that HoursPage is a singleton (max_count = 1)."""
        # The model has max_count = 1
        self.assertEqual(HoursPage.max_count, 1)
