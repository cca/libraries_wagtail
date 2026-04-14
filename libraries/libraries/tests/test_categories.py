"""
Tests for category pages.

This module tests the CategoryPage hierarchy including CategoryPage,
RowComponent, ServicePage, and AboutUsPage.

Test Fixtures:
- CategoryPage under HomePage
- RowComponent children under CategoryPage
- ServicePage under RowComponent

The hierarchy is: CategoryPage → RowComponent → ServicePage/AboutUsPage
"""

from categories.models.pages import CategoryPage, RowComponent, ServicePage

from .base import CMSPageTestCase, CMSSetupMixin
from .utils import PageFactory, create_test_image


class CategoryPageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for category pages with row components."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create CategoryPage as a child of HomePage
        cls.category_page = PageFactory.create_page(
            CategoryPage,
            parent=cls.home,
            title="Services",
            search_description="Library Services",
            published=True,
        )

        # Create RowComponent children
        cls.row_1 = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Research Services",
            summary="<p>Get help with your research</p>",
            published=True,
        )

        cls.row_2 = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Access Services",
            summary="<p>Access materials and spaces</p>",
            published=True,
        )

        cls.row_3 = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Special Collections",
            summary="<p>Explore our unique collections</p>",
            published=True,
        )

        # Create ServicePage children under row_1
        cls.image1 = create_test_image(name="service1.png", size=(400, 200))
        cls.service_page = PageFactory.create_page(
            ServicePage,
            parent=cls.row_1,
            title="Research Consultation",
            search_description="Schedule a research consultation",
            main_image=cls.image1,
            published=True,
        )

    def test_category_page_is_routable(self):
        """Test that the category page can be accessed via URL."""
        self.assertPageIsRoutable(self.category_page)

    def test_category_page_is_renderable(self):
        """Test that the category page renders without errors."""
        self.assertPageIsRenderable(self.category_page)

    def test_category_page_includes_rows(self):
        """Test that the category page displays all published row components."""
        category_url = self.category_page.get_url()
        assert category_url is not None
        response = self.client.get(category_url)
        self.assertEqual(response.status_code, 200)
        # Verify rows context variable exists
        self.assertIn("rows", response.context)
        rows = list(response.context["rows"])
        # All 3 rows should be in the list
        self.assertEqual(len(rows), 3)
        # Check by ID since get_children() returns Page objects
        row_ids = [r.id for r in rows]
        self.assertIn(self.row_1.id, row_ids)
        self.assertIn(self.row_2.id, row_ids)
        self.assertIn(self.row_3.id, row_ids)

    def test_category_page_hierarchy(self):
        """Test that the category page hierarchy is correct."""
        # Verify row_1 is a child of category_page (compare by ID)
        children_ids = [c.id for c in self.category_page.get_children()]
        self.assertIn(self.row_1.id, children_ids)
        # Verify service_page is a child of row_1
        service_children_ids = [c.id for c in self.row_1.get_children()]
        self.assertIn(self.service_page.id, service_children_ids)


class RowComponentTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for row components."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create category page
        cls.category_page = PageFactory.create_page(
            CategoryPage,
            parent=cls.home,
            title="Collections",
            search_description="Library Collections",
            published=True,
        )

        # Create row
        cls.row = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Digital Collections",
            summary="<p>Browse our digital collections</p>",
            published=True,
        )

    def test_row_redirects_to_parent(self):
        """Test that accessing a row directly redirects to its parent CategoryPage."""
        # RowComponent.serve() should redirect to parent
        row_url = self.row.get_url()
        assert row_url is not None
        response = self.client.get(row_url, follow=False)
        # Should redirect (302 or 301)
        self.assertIn(response.status_code, [301, 302])
        # Should redirect to parent category page
        self.assertTrue(response.url.endswith(self.category_page.slug + "/"))

    def test_row_has_summary(self):
        """Test that row components have summary field."""
        self.assertEqual(self.row.summary, "<p>Browse our digital collections</p>")


class ServicePageTests(CMSPageTestCase, CMSSetupMixin):
    """Tests for service pages."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create the hierarchy: CategoryPage → RowComponent → ServicePage
        cls.category_page = PageFactory.create_page(
            CategoryPage,
            parent=cls.home,
            title="Services",
            search_description="Library Services",
            published=True,
        )

        cls.row = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Research Help",
            summary="<p>Research assistance</p>",
            published=True,
        )

        cls.image = create_test_image(name="service.png", size=(400, 200))
        cls.service_page = PageFactory.create_page(
            ServicePage,
            parent=cls.row,
            title="Book a Librarian",
            search_description="Schedule a consultation with a librarian",
            main_image=cls.image,
            published=True,
        )

    def test_service_page_is_routable(self):
        """Test that service pages can be accessed via URL."""
        self.assertPageIsRoutable(self.service_page)

    def test_service_page_is_renderable(self):
        """Test that service pages render without errors."""
        self.assertPageIsRenderable(self.service_page)

    def test_service_page_has_image(self):
        """Test that service pages can have images."""
        self.assertIsNotNone(self.service_page.main_image)
        self.assertEqual(self.service_page.main_image, self.image)

    def test_service_page_parent_hierarchy(self):
        """Test that service pages are properly nested in the hierarchy."""
        # Service page parent should be RowComponent
        service_parent = self.service_page.get_parent()
        assert service_parent is not None
        self.assertEqual(service_parent.specific, self.row)
        # RowComponent parent should be CategoryPage
        row_parent = self.row.get_parent()
        assert row_parent is not None
        self.assertEqual(row_parent.specific, self.category_page)
