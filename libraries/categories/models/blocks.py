from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from wagtail.blocks import (
    ChoiceBlock,
    StructBlock,
    StructValue,
    StreamBlock,
    CharBlock,
    RichTextBlock,
    TextBlock,
    RawHTMLBlock,
    URLBlock,
    PageChooserBlock,
    ListBlock,
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.blocks import ImageChooserBlock


# see docs.wagtail.io/en/v2.6.1/topics/streamfield.html#custom-value-class-for-structblock
class LinkStructValue(StructValue):
    def url(self):
        external_url = self.get("external_url")
        page = self.get("page")
        if external_url:
            return external_url
        elif page:
            return page.url
        return None


# can be external link or internal page
class LinkBlock(StructBlock):
    text = CharBlock(label="Link text", required=True)
    # apparently you cannot validate a StructBlock so impossible to make exactly
    # one of these required
    external_url = URLBlock(label="External URL", required=False)
    page = PageChooserBlock(label="Internal web page", required=False)

    # override clean() method to add custom validation
    def clean(self, value):
        # build up a list of (name, value) tuples to be passed to the StructValue constructor
        result = []
        errors = {}
        for name, val in value.items():
            try:
                result.append((name, self.child_blocks[name].clean(val)))
            except ValidationError as e:
                errors[name] = ErrorList([e])

        if value["external_url"] and value["page"]:
            e = ErrorList(
                [
                    ValidationError(
                        "Links cannot have both an external URL and an internal page."
                    )
                ]
            )
            # we put the error in both the child blocks to aid with display
            errors["external_url"] = errors["page"] = e
        elif not value["external_url"] and not value["page"]:
            e = ErrorList(
                [
                    ValidationError(
                        "Links must have either an external URL or an internal page."
                    )
                ]
            )
            errors["external_url"] = e

        if errors:
            # The message here is arbitrary - StructBlock.render_form will suppress it
            # and delegate the errors contained in the 'params' dict to the child blocks instead
            raise ValidationError("Validation error in StructBlock", params=errors)

        return self._to_struct_value(result)

    class Meta:
        icon = "link"
        template = "categories/blocks/link-block.html"
        value_class = LinkStructValue


class LinkedImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(features=settings.RICHTEXT_BASIC, required=False)
    external_url = URLBlock(
        label="External URL",
        required=False,
        help_text="Only one of these (external URL or internal page) is needed. You can leave both blank if you don't want the image to be linked.",
    )
    page = PageChooserBlock(label="Internal web page", required=False)

    class Meta:
        icon = "image"
        template = "categories/blocks/linked-image.html"
        # we can reuse this from LinkBlock because we also have page, ext URL
        value_class = LinkStructValue


# for Portal-like card with thumbnail image, linked title, & body
class CardBlock(StructBlock):
    thumbnail = ImageChooserBlock(
        help_text="Should be 3x2 aspect ratio but may be stretched if used in a row without an equal distribution. Resized to roughly 345x230."
    )
    link = LinkBlock()
    body = RichTextBlock(features=settings.RICHTEXT_BASIC)

    class Meta:
        icon = "form"
        template = "categories/blocks/card.html"


class SidebarCardBlock(StructBlock):
    image = ImageChooserBlock(
        required=False,
        help_text="Square, resized to 400x400. If you don't specify an image & select a Page below, the Page's Main Image will be used.",
    )
    link = LinkBlock()

    class Meta:
        icon = "form"
        template = "categories/blocks/sidebar-card.html"


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    name = CharBlock(required=False)
    position = CharBlock(required=False, label="Position or affiliation")

    class Meta:
        icon = "openquote"
        template = "categories/blocks/quote.html"


class EmbedHTML(RawHTMLBlock):
    html = RawHTMLBlock(
        "Embed code or raw HTML",
        help_text="Use this sparingly, if possible.",
    )

    class Meta:
        template = "categories/blocks/embed.html"


class ProductGridBlock(ListBlock):

    class Meta:
        help_text = "Grid of images with (optional) links & captions. Grid is rows of three items on desktop-size screens."
        icon = "table"
        template = "categories/blocks/product_grid_block.html"


class ProductGridItemBlock(StructBlock):
    image = ImageChooserBlock()
    external_url = URLBlock(
        label="External URL",
        required=False,
        help_text="Only one of these (external URL or internal page) is needed. You can leave both blank if you don't want the image to be linked.",
    )
    page = PageChooserBlock(label="Internal web page", required=False)
    title = TextBlock(required=False, max_length=30, help_text="Maximum: 30 characters")
    caption = TextBlock(
        help_text="Text will be truncated if input (including title) exceeds allotted space."
    )


# two blocks combined in one row
class RowBlock(StreamBlock):
    distribution = ChoiceBlock(
        blank=False,
        choices=(
            ("left", "left side bigger"),
            ("right", "right side bigger"),
            ("equal", "equal size sides"),
        ),
        min_num=1,
        max_num=1,
    )
    paragraph = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        template="categories/blocks/paragraph.html",
        icon="pilcrow",
    )
    linked_image = LinkedImageBlock()
    card = CardBlock()
    pullquote = PullQuoteBlock()
    # questionable that this should be advanced HTML but we use callouts a lot
    snippet = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        label="Callout",
        template="categories/blocks/snippet.html",
    )

    class Meta:
        help_text = (
            "Use a 'distribution' block to choose how the row's columns are balanced."
        )
        icon = "grip"
        template = "categories/blocks/row.html"


class BaseStreamBlock(StreamBlock):
    subheading = CharBlock(
        icon="title",
        form_classname="title",
        template="categories/blocks/subheading.html",
    )
    paragraph = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        template="categories/blocks/paragraph.html",
        icon="pilcrow",
    )
    linked_image = LinkedImageBlock()
    card = CardBlock()
    image_grid = ProductGridBlock(ProductGridItemBlock(), label="Image grid")
    pullquote = PullQuoteBlock()
    snippet = RichTextBlock(label="Callout", template="categories/blocks/snippet.html")
    html = EmbedHTML(label="Embed code")
    row = RowBlock(max_num=3)
    table = TableBlock()


# AboutUsPage has a much simpler template
class AboutUsStreamBlock(StreamBlock):
    paragraph = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        icon="pilcrow",
    )
