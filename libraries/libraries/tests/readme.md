# CMS Tests Framework

This directory contains reusable tests for the Wagtail CMS, built to run in CI without requiring external services. Tests use Wagtail/Django's `manage.py test`, not `pytest`.

## Structure

- **base.py** - Base test classes, mixins providing reusable utilities
- **test_cms_pages.py** - Example tests for page loading and navigation
- **utils.py** - Utility functions, e.g. a page factory & `create_test_image`

## Running Tests

### Using Django's test runner with test settings

```bash
# All CMS tests
uv run python libraries/manage.py test libraries.tests --settings=libraries.settings.test
# Specific test module
uv run python libraries/manage.py test libraries.tests.test_cms_pages --settings=libraries.settings.test
# Specific test class
uv run python libraries/manage.py test libraries.tests.test_cms_pages.HomePageTests --settings=libraries.settings.test
# Specific test
uv run python libraries/manage.py test libraries.tests.test_cms_pages.HomePageTests.test_home_page_loads --settings=libraries.settings.test
# Verbose output
uv run python libraries/manage.py test libraries.tests -v 2 --settings=libraries.settings.test
# Or set an env var for test settings
export DJANGO_SETTINGS_MODULE=libraries.settings.test
uv run python libraries/manage.py test libraries.tests
```

## Core Components

### CMSPageTestCase

Base test class extending Wagtail's `WagtailPageTestCase` with utilities for testing Wagtail pages. `WagtailPageTestCase` extends Django's `TestCase` and provides specialized assertions for Wagtail-specific functionality.

#### Custom Utilities (from CMSPageTestCase)

- `assert_page_loads(url, expected_status=200)` - Assert a page loads with expected status
- `assert_page_contains(url, content)` - Assert page contains specific content
- `assert_page_not_contains(url, content)` - Assert page does NOT contain specific content
- `assert_page_context(url, context_key)` - Assert context contains a key
- `get_page_by_slug(slug)` - Get a page by its slug
- `get_page_url(page)` - Get the URL for a page

#### Wagtail-Specific Assertions (from WagtailPageTestCase)

These assertions are inherited from `wagtail.test.utils.WagtailPageTestCase` and provide powerful testing capabilities:

- `assertPageIsRoutable(page, route_path="/")` - Assert a page can be routed to without 404
- `assertPageIsRenderable(page, route_path="/", accept_404=False)` - Assert a page renders without errors
- `assertPageIsEditable(page, post_data=None, user=None)` - Assert page edit view works correctly
- `assertPageIsPreviewable(page, mode="", post_data=None)` - Assert page preview works
- `assertCanCreateAt(parent_model, child_model)` - Assert a child page type can be created under a parent
- `assertCanNotCreateAt(parent_model, child_model)` - Assert a child page type cannot be created under a parent
- `assertCanCreate(parent, child_model, data)` - Assert a child can be created with specific POST data
- `assertAllowedParentPageTypes(child_model, parent_models)` - Test allowed parent page types
- `assertAllowedSubpageTypes(parent_model, child_models)` - Test allowed subpage types

For more details on Wagtail test utilities, see the [Wagtail testing documentation](https://docs.wagtail.org/en/stable/advanced_topics/testing.html).

### CMSSetupMixin

Provides utilities for test setup:

- `create_test_page(parent, **kwargs)` - Create a test page
- `publish_page(page)` - Publish a page to make it live

## Adding New Tests

### Simple Page Loading Test

```python
from .base import CMSPageTestCase

class MyPageTests(CMSPageTestCase):
    def test_my_page_loads(self):
        """Test that my page loads successfully."""
        response = self.assert_page_loads("/my-page/")

    def test_my_page_contains_title(self):
        """Test that my page displays a title."""
        self.assert_page_contains("/my-page/", "Page Title")
```

### Using Wagtail-Specific Assertions

```python
from .base import CMSPageTestCase
from my_app.models import MyPage, ParentPage, ChildPage

class MyPageWagtailTests(CMSPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.page = MyPage(title="Test Page")
        root = Page.get_root_nodes().first()
        root.add_child(instance=cls.page)
        cls.page.save()

    def test_page_is_routable(self):
        """Test that the page can be routed to."""
        self.assertPageIsRoutable(self.page)

    def test_page_is_renderable(self):
        """Test that the page renders without errors."""
        self.assertPageIsRenderable(self.page)

    def test_page_is_editable(self):
        """Test that the page edit view works."""
        self.assertPageIsEditable(self.page)

    def test_allowed_parent_types(self):
        """Test what page types can be parents."""
        self.assertAllowedParentPageTypes(ChildPage, {ParentPage})

    def test_can_create_child_under_parent(self):
        """Test that a child can be created under a parent."""
        self.assertCanCreateAt(ParentPage, ChildPage)
```

### Test with Page Setup

```python
from .base import CMSPageTestCase, CMSSetupMixin
from my_app.models import MyPage

class MyPageTests(CMSPageTestCase, CMSSetupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.my_page = MyPage(title="Test Page")
        # Add to page tree
        root = Page.get_root_nodes().first()
        root.add_child(instance=cls.my_page)
        cls.my_page.save()
        # Publish
        cls.my_page = cls.publish_page(cls.my_page)

    def test_page_loads_via_url(self):
        """Test accessing the page by its URL."""
        url = self.my_page.get_url()
        self.assert_page_loads(url)
```

### Test with Custom Assertions

```python
class MyPageTests(CMSPageTestCase):
    def test_page_has_expected_structure(self):
        response = self.assert_page_loads("/my-page/")

        # Use Django's assertion methods on the response
        self.assertIn("expected-css-class", response.content.decode())
        self.assertEqual(response.status_code, 200)
```

## Best Practices

1. **Use WagtailPageTestCase** - All tests extend `WagtailPageTestCase` which provides Wagtail-specific assertions
2. **Use setUpTestData** - Set up fixtures that don't change between tests for better performance
3. **Keep tests focused** - Each test should verify one thing
4. **Use descriptive names** - Test method names should explain what they're testing
5. **Test behavior, not implementation** - Focus on what users see, not internal structure
6. **No external dependencies** - Tests should not rely on search engines, APIs, or external services
7. **Leverage Wagtail assertions** - Use `assertPageIsRoutable`, `assertPageIsRenderable`, etc. for comprehensive page testing
8. **Test page hierarchy** - Use `assertCanCreateAt` and `assertAllowedParentPageTypes` to validate parent/child relationships

## Common Test Scenarios

### Testing page redirects

```python
def test_page_redirects(self):
    response = self.client.get("/old-url/", follow=False)
    self.assertEqual(response.status_code, 301)  # or 302
    self.assertEqual(response.url, "/new-url/")
```

### Testing context variables

```python
def test_page_context_variables(self):
    response = self.assert_page_loads("/my-page/")
    self.assertIn("featured_items", response.context)
    self.assertGreater(len(response.context["featured_items"]), 0)
```

### Testing parent/child relationships

```python
def test_parent_page_children(self):
    response = self.assert_page_loads(self.parent_page.get_url())
    children = self.parent_page.get_children().live()
    self.assertGreater(children.count(), 0)
```

## Extending the Framework

To add custom test utilities for your project:

1. Extend `CMSPageTestCase` in your app's tests
2. Add project-specific helper methods
3. Create app-specific test base classes

Example:

```python
# libraries/my_app/tests.py
from libraries.tests.base import CMSPageTestCase

class MyAppPageTestCase(CMSPageTestCase):
    """Base class for my_app page tests with custom utilities."""

    def assert_page_has_sidebar(self, url):
        response = self.assert_page_loads(url)
        self.assertContains(response, "sidebar-content")
```
