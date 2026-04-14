# CMS Tests Framework

Tests use Django's `manage.py test` (not pytest) and run without external services.

## Running Tests

```bash
# All tests
uv run python libraries/manage.py test libraries.tests --settings=libraries.settings.test
# Specific module/class/test
uv run python libraries/manage.py test libraries.tests.test_blog --settings=libraries.settings.test
# Verbose
uv run python libraries/manage.py test libraries.tests -v 2 --settings=libraries.settings.test
```

## Core Components

### CMSPageTestCase

Base class extending `WagtailPageTestCase`. Key methods:

**Custom utilities:**
- `assert_page_loads(url, expected_status=200)`
- `assert_page_contains(url, content)`
- `assert_page_context(url, context_key)`
- `get_page_by_slug(slug)`

**Wagtail assertions (inherited):**
- `assertPageIsRoutable(page)` - Page accessible without 404
- `assertPageIsRenderable(page)` - Page renders without errors
- `assertCanCreateAt(parent_model, child_model)` - Test page hierarchy
- See [Wagtail docs](https://docs.wagtail.org/en/stable/advanced_topics/testing.html) for full list

### PageFactory

Utility for creating test pages:

```python
from .utils import PageFactory, create_test_image

page = PageFactory.create_page(
    BlogPage,
    parent=cls.home,  # defaults to HomePage
    title="Test Post",
    date=date(2026, 1, 5),
    main_image=create_test_image(),
    published=True,  # publishes immediately
)
```

## Parent/Child Page Testing Patterns

### Pattern 1: Index with Children (Blog, Exhibitions)

Index pages that list children need child pages to render:

```python
class BlogIndexPageTests(CMSPageTestCase, CMSSetupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.blog_index = PageFactory.create_page(
            BlogIndex, parent=cls.home, published=True
        )
        # Create 3+ children for navigation/ordering tests
        cls.post_1 = PageFactory.create_page(
            BlogPage,
            parent=cls.blog_index,
            date=date(2026, 1, 5),
            main_image=create_test_image(),
            published=True,
        )
```

**With Orderable items (Exhibitions):**

```python
# Create page first
exhibit = PageFactory.create_page(ExhibitPage, parent=index, published=True)
# Add Orderable separately
HeaderImage.objects.create(page=exhibit, image=create_test_image(), sort_order=0)
```

### Pattern 2: Multi-Level Hierarchy (Categories)

```python
# Build top-down: HomePage → CategoryPage → RowComponent → ServicePage
category = PageFactory.create_page(CategoryPage, parent=cls.home, published=True)
row = PageFactory.create_page(RowComponent, parent=category, published=True)
service = PageFactory.create_page(ServicePage, parent=row, published=True)

# Verify hierarchy (compare by ID, not object)
children_ids = [c.id for c in category.get_children()]
self.assertIn(row.id, children_ids)
```

### Pattern 3: Singleton Pages (Hours)

Pages with `max_count = 1` deep in hierarchy:

```python
# Build required parent structure first
category = PageFactory.create_page(CategoryPage, parent=cls.home, published=True)
row = PageFactory.create_page(RowComponent, parent=category, published=True)
hours = PageFactory.create_page(HoursPage, parent=row, published=True)
```

## Type Checking

Handle optional return types for type checkers:

```python
# get_url() returns str | None
page_url = self.page.get_url()
assert page_url is not None  # type guard
response = self.client.get(page_url)

# get_parent() returns Page | None
parent = self.page.get_parent()
assert parent is not None
self.assertEqual(parent.specific, expected_parent)
```

**Why:** Use `assert ... is not None` (not `assertIsNotNone`) as it acts as a type guard.

## Best Practices

1. Use `setUpTestData` for fixtures that don't change between tests
2. Test behavior, not implementation
3. Use descriptive test names
4. Leverage Wagtail assertions (`assertPageIsRoutable`, etc.)
5. Handle optional types with `assert ... is not None`
6. Create realistic parent/child structures matching production
7. Always publish pages when testing live site behavior

## Reference Examples

- **test_blog.py** - Index/child with navigation (12 tests)
- **test_exhib.py** - Orderable images (9 tests)
- **test_categories.py** - Multi-level hierarchy (10 tests)
- **test_hours.py** - Singleton page (5 tests)

## Common Patterns

```python
# Test context variables
response = self.client.get(page_url)
self.assertIn("my_var", response.context)

# Test redirects
response = self.client.get(url, follow=False)
self.assertIn(response.status_code, [301, 302])

# Test parent/child relationships
children = parent.get_children().live()
self.assertGreater(children.count(), 0)
```
