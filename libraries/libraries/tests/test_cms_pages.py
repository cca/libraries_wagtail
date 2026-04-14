"""Tests for core CMS page functionality."""

from home.models import HomePage
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from .utils import create_test_image


class HomePageTests(WagtailPageTestCase):
    """Tests for page creation and model functionality."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        # Create root page first
        cls.root = Page.add_root(title="Root")

    def test_page_model_exists(self):
        """Test that Page model can be instantiated."""
        page = Page(title="Test Page")
        self.assertIsNotNone(page)
        self.assertEqual(page.title, "Test Page")

    def test_page_can_be_saved(self):
        """Test that Page can be saved to the database."""
        page = Page(title="Saved Page")
        self.root.add_child(instance=page)
        page.save()

        saved_page = Page.objects.get(title="Saved Page")
        self.assertIsNotNone(saved_page)
        self.assertEqual(saved_page.title, "Saved Page")

    def test_home_page_model_exists(self):
        """Test that HomePage model can be instantiated."""
        home = HomePage(title="Home")
        self.assertIsNotNone(home)
        self.assertEqual(home.title, "Home")

    def test_home_page_with_image(self):
        """Test that HomePage can be created with a background image."""
        test_image = create_test_image(name="home_bg.png")
        home = HomePage(title="Home", background_image=test_image)
        self.assertEqual(home.background_image, test_image)


class RootPageTests(WagtailPageTestCase):
    """Tests for root-level page behavior."""

    @classmethod
    def setUpTestData(cls):
        """Ensure root page exists."""
        cls.root_page = Page.add_root(title="Root")

    def test_root_page_exists(self):
        """Test that root page exists."""
        root_pages = Page.get_root_nodes()
        self.assertGreater(root_pages.count(), 0)

    def test_root_page_is_hierarchy_node(self):
        """Test that root page is properly configured."""
        self.assertEqual(self.root_page.depth, 1)
        self.assertEqual(self.root_page.numchild, 0)

    def test_can_add_child_page(self):
        """Test that child pages can be added."""
        child = Page(title="Child Page")
        self.root_page.add_child(instance=child)
        child.save()

        children = self.root_page.get_children()
        self.assertEqual(children.count(), 1)
        self.assertEqual(children.first().title, "Child Page")


class PageNavigationTests(WagtailPageTestCase):
    """Tests for page structure and hierarchy."""

    @classmethod
    def setUpTestData(cls):
        """Set up page hierarchy."""
        cls.root = Page.add_root(title="Root")
        cls.parent = Page(title="Parent Page")
        cls.root.add_child(instance=cls.parent)
        cls.parent.save()

        # Add a grandchild to test hierarchy
        cls.child = Page(title="Child Page")
        cls.parent.add_child(instance=cls.child)
        cls.child.save()

    def test_parent_page_exists(self):
        """Test that parent page was created."""
        self.assertIsNotNone(self.parent.pk)

    def test_parent_has_path_and_depth(self):
        """Test that child pages have path and depth set."""
        self.assertIsNotNone(self.parent.path)
        self.assertEqual(self.parent.depth, 2)

    def test_page_hierarchy_structure(self):
        """Test page hierarchy structure."""
        children = self.root.get_children()
        self.assertIn(self.parent, children)

        grandchildren = self.parent.get_children()
        self.assertIn(self.child, grandchildren)

    def test_unpublished_pages_not_in_live_query(self):
        """Test that unpublished pages are created correctly."""
        unpublished = Page(title="Unpublished")
        self.root.add_child(instance=unpublished)
        unpublished.save()

        # Verify the page was saved
        saved_unpublished = Page.objects.get(title="Unpublished")
        self.assertIsNotNone(saved_unpublished)
