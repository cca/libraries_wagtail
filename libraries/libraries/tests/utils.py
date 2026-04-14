"""Common utility functions for CMS tests."""

from io import BytesIO
from typing import Type

from django.core.files.images import ImageFile
from PIL import Image as PILImage
from wagtail.images.models import Image
from wagtail.models import Page


class PageFactory:
    """Factory for creating test pages of various types."""

    @staticmethod
    def create_page(
        page_class: Type[Page],
        parent: Page | None = None,
        published: bool = False,
        **kwargs,
    ) -> Page:
        """
        Create a page of the specified type.

        Args:
            page_class: The Page subclass to instantiate
            parent: Parent page (defaults to root if None)
            published: Whether to publish the page immediately
            **kwargs: Additional fields to set on the page

        Returns:
            The created and saved (and optionally published) page
        """
        if parent is None:
            parent = Page.get_root_nodes().first()  # type: ignore
            if parent is None:
                parent = Page.add_root(title="Root")

        assert parent is not None, "Root page must exist to create test pages"
        # Set default title if not provided
        if "title" not in kwargs:
            kwargs["title"] = f"Test {page_class.__name__}"

        page = page_class(**kwargs)
        parent.add_child(instance=page)
        page.save()

        if published:
            page.save_revision().publish()

        return page


def get_or_create_root_page() -> Page:
    """
    Get the root page, creating one if it doesn't exist.

    Returns:
        The root Page object
    """
    root = Page.get_root_nodes().first()
    if root is None:
        root = Page.add_root(title="Root")
    assert isinstance(root, Page), "Failed to create root page"
    return root


def publish_page(page: Page) -> Page:
    """
    Publish a page and return it.

    Args:
        page: The page to publish

    Returns:
        The page instance
    """
    page.save_revision().publish()
    return page


def unpublish_page(page: Page) -> Page:
    """
    Unpublish a page.

    Args:
        page: The page to unpublish

    Returns:
        The page instance
    """
    page.unpublish()
    return page


def get_page_tree_structure() -> dict:
    """
    Get the current page tree structure for debugging.

    Useful for understanding the page hierarchy during test failures.

    Returns:
        Dictionary representing the page tree
    """

    def _build_tree(page):
        return {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "live": page.live,
            "children": [_build_tree(child) for child in page.get_children()],
        }

    root_pages = Page.get_root_nodes()
    return {"roots": [_build_tree(root) for root in root_pages]}


def create_test_image(name: str = "test.png", size: tuple = (100, 100)) -> Image:
    """
    Create a test image for use in tests.

    Args:
        name: Image filename
        size: Tuple of (width, height) in pixels

    Returns:
        Wagtail Image instance
    """
    # Create a simple PIL image
    pil_image = PILImage.new("RGB", size, color="red")
    image_io = BytesIO()
    pil_image.save(image_io, format="PNG")
    image_io.seek(0)

    # Create Wagtail Image object
    image_file = ImageFile(image_io, name=name)
    wagtail_image = Image(title=name, file=image_file)
    wagtail_image.save()

    return wagtail_image
