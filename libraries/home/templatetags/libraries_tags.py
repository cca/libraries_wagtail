""" All the CCA Libraries' custom template tags

See: https://docs.djangoproject.com/en/2.2/howto/custom-template-tags/
"""

import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def condense_whitespace(value):
    """convert tabs & linebreaks into single spaces"""
    return re.sub(r"\s+", " ", re.sub(r"[\n\t]+", " ", value))


@register.filter
@stringfilter
def stripjs(value):
    """strip <script> tags from HTML content
    stackoverflow.com/questions/6444893/strip-javascript-code-before-rendering-in-django-templates
    """
    stripped = re.sub(
        r"<script(?:\s[^>]*)?(>(?:.(?!/script>))*</script>|/>)", "", value, flags=re.S
    )
    return mark_safe(stripped)
