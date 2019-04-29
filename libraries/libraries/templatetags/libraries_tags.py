""" All the CCA Libraries' custom template tags

See: https://docs.djangoproject.com/en/2.2/howto/custom-template-tags/
"""
import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def condense_whitespace(value):
    """ convert tabs & linebreaks into single spaces """
    return re.sub(r'\s+', ' ', re.sub(r'[\n\t]+', ' ', value) )
